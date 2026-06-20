#!/usr/bin/env python3
"""
Data ingestion script: fetches trials from ClinicalTrials.gov and indexes them in ChromaDB
"""

import os
import time
import json
import httpx
from dotenv import load_dotenv
from vector_store import VectorStore
from sentence_transformers import SentenceTransformer

# Load environment variables from parent directory
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))

CHROMA_PATH = os.getenv("CHROMA_PATH", "./chroma_db")

# Initialize embeddings model (runs locally, no API key needed)
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

# Initialize vector store
vector_store = VectorStore(path=CHROMA_PATH)


def split_into_chunks(text: str, max_chars: int = 1500, overlap_chars: int = 200) -> list[str]:
    """Split text into chunks with overlap (character-based, no token counter needed)"""
    if not text:
        return []
    
    chunks = []
    stride = max_chars - overlap_chars
    
    for i in range(0, len(text), stride):
        chunk_text = text[i:i + max_chars]
        if chunk_text.strip():
            chunks.append(chunk_text)
    
    return chunks if chunks else [text]


def extract_sections(eligibility_text: str) -> dict:
    """Split eligibility criteria into inclusion and exclusion sections"""
    inclusion_text = ""
    exclusion_text = ""
    
    # Look for "Inclusion" and "Exclusion" sections
    lower_text = eligibility_text.lower()
    
    inclusion_idx = lower_text.find("inclusion")
    exclusion_idx = lower_text.find("exclusion")
    
    if inclusion_idx != -1:
        if exclusion_idx != -1:
            inclusion_text = eligibility_text[inclusion_idx:exclusion_idx]
            exclusion_text = eligibility_text[exclusion_idx:]
        else:
            inclusion_text = eligibility_text[inclusion_idx:]
    elif exclusion_idx != -1:
        exclusion_text = eligibility_text[exclusion_idx:]
    else:
        # If no clear sections, treat all as general criteria
        inclusion_text = eligibility_text
    
    return {
        "inclusion": inclusion_text.strip(),
        "exclusion": exclusion_text.strip()
    }


def embed_text(text: str) -> list[float]:
    """Get embedding for text using sentence-transformers (local, no API key needed)"""
    embeddings = embedding_model.encode(text, convert_to_numpy=False)
    return embeddings.tolist() if hasattr(embeddings, 'tolist') else embeddings


def fetch_trials():
    """Fetch trials from ClinicalTrials.gov REST API v2"""
    url = "https://clinicaltrials.gov/api/v2/studies"
    
    params = {
        "filter.overallStatus": "RECRUITING",
        "query.term": "",
        "pageSize": 200,  # max allowed is 200, not 1000
        "format": "json"
    }
    
    all_studies = []
    next_page_token = None
    page_count = 0
    
    try:
        print("Fetching trials from ClinicalTrials.gov...")
        while len(all_studies) < 1000:
            if next_page_token:
                params["pageToken"] = next_page_token
            
            page_count += 1
            print(f"Fetching page {page_count}...")
            response = httpx.get(url, params=params, timeout=30)
            
            if response.status_code != 200:
                print(f"API returned status {response.status_code}: {response.text}")
                break
            
            data = response.json()
            studies = data.get("studies", [])
            
            if not studies:
                print("No more studies found.")
                break
            
            all_studies.extend(studies)
            print(f"Fetched {len(all_studies)} trials so far...")
            
            next_page_token = data.get("nextPageToken")
            if not next_page_token:
                print("No more pages available.")
                break
            
            time.sleep(0.3)  # be polite to the API
        
        return all_studies
    
    except Exception as e:
        print(f"Error fetching trials: {e}")
        import traceback
        traceback.print_exc()
        return []


def ingest_trials():
    """Main ingest function"""
    print(f"Using vector store path: {CHROMA_PATH}")
    
    # Check if collection already has data
    existing_count = vector_store.count()
    if existing_count > 0:
        print(f"Vector store already has {existing_count} documents. Skipping ingest (idempotent).")
        return
    
    print("Starting trial ingestion...")
    studies = fetch_trials()
    
    if not studies:
        print("No trials fetched. Exiting.")
        return
    
    print(f"Processing {len(studies)} trials...")
    
    total_chunks = 0
    
    for idx, study in enumerate(studies):
        if (idx + 1) % 100 == 0:
            print(f"Progress: {idx + 1}/{len(studies)} trials processed")
        
        try:
            # Extract trial data using correct v2 API response structure
            protocol = study.get("protocolSection", {})
            id_module = protocol.get("identificationModule", {})
            eligibility_module = protocol.get("eligibilityModule", {})
            conditions_module = protocol.get("conditionsModule", {})
            design_module = protocol.get("designModule", {})
            sponsor_module = protocol.get("sponsorCollaboratorsModule", {})
            
            nct_id = id_module.get("nctId", "")
            title = id_module.get("briefTitle", "")
            conditions = conditions_module.get("conditions", [])
            eligibility_criteria = eligibility_module.get("eligibilityCriteria", "")
            phase = design_module.get("phases", [])
            sponsor = sponsor_module.get("leadSponsor", {}).get("name", "")
            
            if not nct_id or not title or not eligibility_criteria:
                continue
            
            # Normalize phase (convert list to string)
            if isinstance(phase, list):
                phase = ", ".join(phase) if phase else "Unknown"
            
            # Split eligibility criteria
            sections = extract_sections(eligibility_criteria)
            
            # Chunk and embed each section
            doc_ids = []
            documents = []
            embeddings = []
            metadatas = []
            
            for section_type, section_text in sections.items():
                if section_text.strip():
                    chunks = split_into_chunks(section_text)
                    
                    for chunk_num, chunk in enumerate(chunks):
                        doc_id = f"{nct_id}_{section_type}_{chunk_num}"
                        
                        # Embed chunk
                        embedding = embed_text(chunk)
                        
                        doc_ids.append(doc_id)
                        documents.append(chunk)
                        embeddings.append(embedding)
                        metadatas.append({
                            "nct_id": nct_id,
                            "title": title,
                            "conditions": json.dumps(conditions),
                            "phase": phase,
                            "sponsor": sponsor,
                            "chunk_type": section_type
                        })
                        
                        total_chunks += 1
            
            # Add to vector store
            if doc_ids:
                vector_store.add_documents(documents, embeddings, doc_ids, metadatas)
        
        except Exception as e:
            print(f"Error processing trial {nct_id}: {e}")
            continue
    
    print(f"\nIngestion complete!")
    print(f"Total trials: {len(studies)}")
    print(f"Total chunks indexed: {total_chunks}")
    print(f"Vector store now contains: {vector_store.count()} documents")


if __name__ == "__main__":
    ingest_trials()
