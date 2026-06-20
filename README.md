# ClinicalTrialCompass

An AI-powered web app that matches patients to relevant open clinical trials using a 3-pass LLM pipeline and RAG over ClinicalTrials.gov data.

## Features

- **Intelligent Patient Matching**: Uses Groq's Mixtral-8x7b LLM to synthesize patient profiles and match them against clinical trials
- **3-Pass Pipeline**:
  - Pass 2a: Semantic query synthesis from patient profile
  - Pass 2b: Vector retrieval of candidate trials using ChromaDB
  - Pass 3: Re-ranking, explanation, and uncertainty flagging
- **Rich Eligibility Analysis**: Evaluates each trial criterion against the patient profile
- **Data Gaps Awareness**: Flags missing or ambiguous data that affects eligibility
- **Real-time Trial Data**: Indexed from ClinicalTrials.gov REST API v2

## Tech Stack

### Backend
- **Framework**: FastAPI + Uvicorn
- **LLM**: Groq (Mixtral-8x7b) via Python SDK
- **Embeddings**: sentence-transformers with all-MiniLM-L6-v2 (local, no API key required)
- **Vector DB**: ChromaDB (local, persistent)
- **Structured Output**: instructor + Pydantic
- **Data Source**: ClinicalTrials.gov REST API v2

### Frontend
- **Framework**: React 18 (Vite)
- **Styling**: Tailwind CSS
- **HTTP Client**: Axios

## Installation & Setup

### Prerequisites
- Python 3.9+
- Node.js 16+
- Groq API key (free tier available at https://console.groq.com)

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create or update `.env` file in the backend directory:
   ```
   GROQ_API_KEY=your_groq_api_key_here
   CHROMA_PATH=./chroma_db
   ```

4. Run the ingestion script (one time, ~5-10 minutes):
   ```bash
   python ingest.py
   ```
   This fetches and indexes ~3000 recruiting Phase II/III trials from ClinicalTrials.gov.

5. Start the FastAPI server:
   ```bash
   uvicorn main:app --reload
   ```
   The server will be available at `http://localhost:8000`

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Create `.env.local` file in the frontend directory:
   ```
   VITE_API_URL=http://localhost:8000
   ```

4. Start the development server:
   ```bash
   npm run dev
   ```
   The app will be available at `http://localhost:5173`

## Usage

1. Open `http://localhost:5173` in your browser
2. Fill in or load the sample patient profile
3. Click "Find Matching Trials"
4. View the ranked results with eligibility breakdowns

## Project Structure

```
clinicaltrial-compass/
├── backend/
│   ├── main.py               # FastAPI app and routes
│   ├── pipeline.py           # 3-pass LLM pipeline logic
│   ├── ingest.py             # Trial data ingestion script
│   ├── models.py             # Pydantic schemas
│   ├── vector_store.py       # ChromaDB wrapper
│   └── requirements.txt       # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── App.jsx           # Main app state machine
│   │   ├── api.js            # axios API client
│   │   ├── main.jsx          # React entry point
│   │   ├── index.css         # Tailwind CSS
│   │   └── components/
│   │       ├── PatientForm.jsx      # Patient data entry
│   │       ├── LoadingStepper.jsx   # 3-step progress UI
│   │       ├── ProfileCard.jsx      # Patient profile summary
│   │       ├── MatchCard.jsx        # Individual trial result
│   │       └── CaveatBadge.jsx      # Data gap warnings
│   ├── index.html            # HTML entry point
│   ├── vite.config.js        # Vite configuration
│   ├── tailwind.config.js    # Tailwind CSS config
│   ├── postcss.config.js     # PostCSS config
│   ├── package.json          # Node.js dependencies
│   └── .gitignore
├── .env                      # Environment configuration
└── README.md                 # This file
```

## API Endpoints

### POST /match
Matches a patient to relevant clinical trials.

**Request:**
```json
{
  "age": 58,
  "sex": "Female",
  "primary_diagnosis": "Non-small cell lung cancer (NSCLC)",
  "stage_or_severity": "Stage II",
  "molecular_markers": "EGFR exon 19 deletion (positive)",
  "prior_treatments": "None",
  "current_medications": "Lisinopril 10mg, Metformin 500mg",
  "performance_status": "ECOG 1",
  "additional_notes": "No brain metastases on recent MRI"
}
```

**Response:**
```json
{
  "patient_profile": { ... },
  "matches": [
    {
      "nct_id": "NCT04123456",
      "title": "Trial of XYZ for NSCLC",
      "phase": "Phase III",
      "conditions": ["Non-small cell lung cancer"],
      "match_score": 87,
      "match_narrative": "...",
      "criterion_verdicts": [...],
      "caveats": ["Performance status verification needed"],
      "trial_url": "https://clinicaltrials.gov/study/NCT04123456"
    }
  ]
}
```

### GET /health
Health check endpoint.

**Response:**
```json
{
  "status": "ok",
  "trials_indexed": 3000
}
```

## Important Notes

- The ingestion script (`ingest.py`) is idempotent—re-running it will not create duplicate embeddings
- ChromaDB data persists locally in `./chroma_db` and survives server restarts
- The 3-pass pipeline uses synchronous calls for simplicity and debuggability
- LLM prompts explicitly instruct the model not to assume information outside the patient profile
- Match scores range from 0-100; caveats flag missing data that affects accuracy
- **No hidden costs**: Embeddings are computed locally using sentence-transformers (no API calls), only Groq LLM calls are billable (Groq has a free tier)

## Development

### Running Tests
Currently no test suite included. Recommended additions:
- Unit tests for pipeline components
- Integration tests for API endpoints
- End-to-end tests for the full flow

### Extending the Project
- Add authentication/user accounts
- Persist search history
- Add trial filtering UI
- Support for PDF uploads (eligibility documents)
- Alternative vector stores (Pinecone, Weaviate)
- Scheduled re-ingestion of trial data

## License

MIT

## Support

For issues or questions, please open a GitHub issue.
