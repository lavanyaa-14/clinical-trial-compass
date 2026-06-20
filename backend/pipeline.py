"""
3-pass LLM pipeline for clinical trial matching
"""

import os
import json
import time
import instructor
from groq import Groq
from dotenv import load_dotenv
from models import PatientProfile, TrialMatch, CriterionVerdict
from vector_store import VectorStore
from sentence_transformers import SentenceTransformer

# Load environment variables from parent directory
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
CHROMA_PATH = os.getenv("CHROMA_PATH", "./chroma_db")

# Debug: check if API key is loaded
print("GROQ KEY LOADED:", GROQ_API_KEY is not None)
if not GROQ_API_KEY:
    print("WARNING: GROQ_API_KEY not found in .env file!")
    print("Current working directory:", os.getcwd())
    print("Looking for .env at:", os.path.join(os.path.dirname(__file__), "..", ".env"))

# Initialize embeddings model (runs locally)
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

# Initialize Groq client with instructor
groq_client = Groq(api_key=GROQ_API_KEY)
client = instructor.from_groq(groq_client, mode=instructor.Mode.JSON)

vector_store = VectorStore(path=CHROMA_PATH)


def pass_2a_synthesize_query(patient_profile: PatientProfile) -> str:
    """
    Pass 2a: Generate a semantic search query from patient profile
    """
    system_prompt = """You are a clinical research expert. Given a patient profile, write a single
descriptive paragraph that captures what clinical trial would be ideal for this patient.
Focus on diagnosis, stage, molecular markers, and treatment history.
This will be used as a semantic search query. Return only the paragraph, no additional text."""
    
    user_prompt = f"""Patient profile:
{json.dumps(patient_profile.model_dump(), indent=2)}"""
    
    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.5
    )
    
    return response.choices[0].message.content.strip()


def pass_2b_retrieve_trials(query: str) -> list[dict]:
    """
    Pass 2b: Retrieve candidate trials from ChromaDB using semantic search
    1. Embed the query
    2. Query ChromaDB for top 15 results
    3. Group by nct_id and concatenate chunks
    4. Return list of trial candidates
    """
    # Embed the query using sentence-transformers
    query_embedding = embedding_model.encode(query, convert_to_numpy=False)
    if hasattr(query_embedding, 'tolist'):
        query_embedding = query_embedding.tolist()
    
    # Query ChromaDB
    results = vector_store.query(embedding=query_embedding, n_results=15)
    
    # Group by nct_id
    trial_map = {}
    
    if results and results["ids"] and len(results["ids"]) > 0:
        for i, doc_id in enumerate(results["ids"][0]):
            metadata = results["metadatas"][0][i]
            document = results["documents"][0][i]
            
            nct_id = metadata["nct_id"]
            
            if nct_id not in trial_map:
                trial_map[nct_id] = {
                    "nct_id": nct_id,
                    "title": metadata["title"],
                    "conditions": json.loads(metadata.get("conditions", "[]")),
                    "phase": metadata["phase"],
                    "sponsor": metadata.get("sponsor", ""),
                    "eligibility_text": ""
                }
            
            trial_map[nct_id]["eligibility_text"] += "\n" + document
    
    return list(trial_map.values())


def pass_3_rerank_and_explain(patient_profile: PatientProfile, 
                              candidate_trials: list[dict]) -> list[TrialMatch]:
    """
    Pass 3: Re-rank, explain, and flag uncertainty
    Uses instructor for structured JSON output
    """
    system_prompt = """You are a clinical trial matching expert. For each trial, evaluate whether
the patient meets the eligibility criteria. Go criterion by criterion.
Be precise — do not assume information that is not stated in the patient profile.
If a criterion requires information not present in the profile, mark it as 'unclear' 
and add it to caveats. Return only valid JSON."""
    
    # Format candidate trials for the prompt
    trials_text = ""
    for i, trial in enumerate(candidate_trials):
        trials_text += f"""
Trial {i+1}:
- NCT ID: {trial['nct_id']}
- Title: {trial['title']}
- Phase: {trial['phase']}
- Conditions: {', '.join(trial['conditions'])}
- Eligibility Criteria:
{trial['eligibility_text']}

"""
    
    user_prompt = f"""Patient profile:
{json.dumps(patient_profile.model_dump(), indent=2)}

Candidate trials:
{trials_text}

For each trial, evaluate the match and return:
- match_score (0-100): how well the patient fits overall
- match_narrative: 2-4 sentence plain English explanation
- criterion_verdicts: list of {{criterion, verdict ("meets"|"does_not_meet"|"unclear"), reason}} for key eligibility criteria
- caveats: list of missing/ambiguous data items that affect eligibility assessment
- trial_url: https://clinicaltrials.gov/study/{{nct_id}}

Return a JSON array of all trials with these fields, sorted by match_score descending.
Return only the top 5 trials by match_score.
Return ONLY valid JSON, with no additional text."""
    
    try:
        result = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            response_model=list[TrialMatch],
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.1,  # low temperature for more consistent structured output
            max_retries=2
        )
        
        # Sort by match_score descending and take top 5
        sorted_matches = sorted(result, key=lambda x: x.match_score, reverse=True)[:5]
        return sorted_matches
    
    except Exception as e:
        print(f"Error in Pass 3: {e}")
        raise


def run_pipeline(patient_profile: PatientProfile) -> list[TrialMatch]:
    """
    Run the complete 3-pass pipeline
    """
    start_time = time.time()
    
    # Pass 2a: Synthesize query
    print("[Pipeline] Pass 2a: Synthesizing search query...")
    query_time = time.time()
    semantic_query = pass_2a_synthesize_query(patient_profile)
    print(f"  Query: {semantic_query[:100]}...")
    print(f"  Time: {time.time() - query_time:.2f}s")
    
    # Pass 2b: Retrieve trials
    print("[Pipeline] Pass 2b: Retrieving candidate trials...")
    retrieval_time = time.time()
    candidate_trials = pass_2b_retrieve_trials(semantic_query)
    print(f"  Retrieved: {len(candidate_trials)} trials")
    print(f"  Time: {time.time() - retrieval_time:.2f}s")
    
    if not candidate_trials:
        raise ValueError("No trials found in ChromaDB. Run ingest.py first.")
    
    # Pass 3: Re-rank and explain
    print("[Pipeline] Pass 3: Ranking and explaining matches...")
    ranking_time = time.time()
    matches = pass_3_rerank_and_explain(patient_profile, candidate_trials)
    print(f"  Ranked: {len(matches)} top matches")
    print(f"  Time: {time.time() - ranking_time:.2f}s")
    
    total_time = time.time() - start_time
    print(f"[Pipeline] Total time: {total_time:.2f}s")
    
    return matches
