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







