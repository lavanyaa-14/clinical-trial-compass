from pydantic import BaseModel
from typing import Literal


class PatientProfile(BaseModel):
    age: int
    sex: str  # "Male" | "Female" | "Other"
    primary_diagnosis: str
    stage_or_severity: str  # e.g. "Stage II", "Moderate", "N/A"
    molecular_markers: str  # e.g. "EGFR exon 19 deletion" or "None known"
    prior_treatments: str  # e.g. "None" or "Carboplatin, 2 cycles"
    current_medications: str  # e.g. "Lisinopril 10mg, Metformin 500mg"
    performance_status: str  # e.g. "ECOG 1" or "Unknown"
    additional_notes: str  # any other relevant clinical info


class CriterionVerdict(BaseModel):
    criterion: str
    verdict: Literal["meets", "does_not_meet", "unclear"]
    reason: str


class TrialMatch(BaseModel):
    nct_id: str
    title: str
    phase: str
    conditions: list[str]
    match_score: int  # 0-100
    match_narrative: str  # 2-4 sentence plain English explanation
    criterion_verdicts: list[CriterionVerdict]
    caveats: list[str]  # items where patient data is missing/ambiguous
    trial_url: str  # f"https://clinicaltrials.gov/study/{nct_id}"


class MatchResponse(BaseModel):
    patient_profile: PatientProfile
    matches: list[TrialMatch]  # top 5, sorted by match_score desc
