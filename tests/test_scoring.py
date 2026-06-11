from app.utils.helpers import (
    days_since, text_lower, skill_names, skill_map,
    proficiency_score, proficiency_with_endorsements,
    education_tier_score, career_text, summary_text, full_text
)
from app.services.scoring import (
    score_skills, score_career, score_disqualifiers,
    score_behavioral, score_candidate
)

# ── HELPER TESTS (7 tests) ───────────────────────────────────────────────────

def test_helpers_days_since():
    # Null or invalid strings
    assert days_since(None) == 9999
    assert days_since("") == 9999
    assert days_since("invalid-date") == 9999
    # Valid date
    assert days_since("2026-06-01") == 10

def test_helpers_text_lower():
    assert text_lower(None) == ""
    assert text_lower("Hello WORLD") == "hello world"

def test_helpers_skill_names_and_map():
    cand = {"skills": [{"name": "Python"}, {"name": "RAG"}]}
    assert skill_names(cand) == ["python", "rag"]
    
    s_map = skill_map(cand)
    assert "python" in s_map
    assert s_map["python"]["name"] == "Python"

def test_helpers_proficiency_score():
    assert proficiency_score("expert") == 1.0
    assert proficiency_score("Advanced") == 0.8
    assert proficiency_score("intermediate") == 0.5
    assert proficiency_score("beginner") == 0.2
    assert proficiency_score("unknown") == 0.3
    assert proficiency_score(None) == 0.3

def test_helpers_proficiency_with_endorsements():
    # Endorsement boosts
    s1 = {"proficiency": "expert", "endorsements": 50, "duration_months": 24}
    assert proficiency_with_endorsements(s1) == 1.0 # capped at 1.0
    
    s2 = {"proficiency": "intermediate", "endorsements": 20, "duration_months": 12}
    assert proficiency_with_endorsements(s2) == 0.55 # 0.5 + 0.05
    
    # Anomaly penalty
    s3 = {"proficiency": "expert", "endorsements": 0, "duration_months": 3}
    assert proficiency_with_endorsements(s3) == 0.85 # 1.0 - 0.15

def test_helpers_education_tier_score():
    c_empty = {}
    assert education_tier_score(c_empty) == 0.5
    
    c_t1 = {"education": [{"tier": "tier_1"}, {"tier": "tier_4"}]}
    assert education_tier_score(c_t1) == 1.0
    
    c_t3 = {"education": [{"tier": "tier_3"}]}
    assert education_tier_score(c_t3) == 0.55

def test_helpers_text_extractions():
    cand = {
        "profile": {"summary": "summary_here", "headline": "headline_here"},
        "career_history": [{"title": "Eng", "company": "Co", "description": "Desc"}],
        "skills": [{"name": "Python"}],
        "certifications": [{"name": "Cert"}]
    }
    assert "summary_here" in summary_text(cand)
    assert "eng co desc" in career_text(cand)
    assert "python" in full_text(cand)
    assert "cert" in full_text(cand)

# ── SCORING TESTS (18 tests) ─────────────────────────────────────────────────

def test_score_skills_empty():
    cand = {}
    assert score_skills(cand) == 0.0

def test_score_skills_must_have():
    # Candidate with MUST_HAVE skills and Python
    cand = {
        "skills": [
            {"name": "FAISS", "proficiency": "expert"},
            {"name": "Python", "proficiency": "advanced"}
        ]
    }
    score = score_skills(cand)
    assert score > 0.0
    # Must be between 0 and 1.0
    assert 0.0 <= score <= 1.0

def test_score_skills_with_assessments():
    cand = {
        "skills": [
            {"name": "Pinecone", "proficiency": "expert"}
        ],
        "redrob_signals": {
            "skill_assessment_scores": {"Pinecone": 90}
        }
    }
    score = score_skills(cand)
    assert score > 0.0

def test_score_career_empty():
    cand = {}
    assert score_career(cand) == 0.0

def test_score_career_yoe_scoring():
    # Ideal range 5-9 YoE
    c1 = {
        "profile": {"years_of_experience": 7},
        "career_history": [{"description": "Built and shipped a production recommendation syst"}]
    }
    s1 = score_career(c1)
    
    # Manager range >12 YoE
    c2 = {
        "profile": {"years_of_experience": 15},
        "career_history": [{"description": "Built and shipped a production recommendation syst"}]
    }
    s2 = score_career(c2)
    assert s1 > s2

def test_score_career_unsupported_template():
    # Disqualifies if no matched career template
    cand = {
        "profile": {"years_of_experience": 7},
        "career_history": [{"description": "Irrelevant sales script here"}]
    }
    assert score_career(cand) == 0.0

def test_score_disqualifiers_location():
    # Outside India = disqualified
    c_us = {"profile": {"country": "united states"}}
    assert score_disqualifiers(c_us) == 0.0
    
    c_in = {"profile": {"country": "india"}}
    assert score_disqualifiers(c_in) == 1.0

def test_score_disqualifiers_consulting():
    # Consulting-firm only = disqualified
    cand = {
        "profile": {"country": "india"},
        "career_history": [
            {"company": "TCS"},
            {"company": "Wipro"}
        ]
    }
    assert score_disqualifiers(cand) == 0.0

def test_score_disqualifiers_consulting_mixed():
    # Mixed services + product = allowed (needs a production keyword to avoid research penalty)
    cand = {
        "profile": {"country": "india", "summary": "shipped production systems"},
        "career_history": [
            {"company": "TCS"},
            {"company": "Zomato"}
        ]
    }
    assert score_disqualifiers(cand) == 1.0

def test_score_disqualifiers_bad_title():
    # Bad title with no ML history = disqualified
    cand = {
        "profile": {"country": "india", "current_title": "Marketing Manager"},
        "career_history": [
            {"title": "Sales Coordinator", "description": "Selling ads"}
        ]
    }
    assert score_disqualifiers(cand) == 0.0

def test_score_disqualifiers_bad_title_with_ml_history():
    # Bad title but has ML history = allowed (needs a production keyword to avoid research penalty)
    cand = {
        "profile": {"country": "india", "current_title": "Marketing Manager", "summary": "deployed in production"},
        "career_history": [
            {"title": "Machine Learning Engineer", "description": "built RAG"}
        ]
    }
    assert score_disqualifiers(cand) == 1.0

def test_score_disqualifiers_keyword_stuffer():
    # 30+ skills but very short career history
    cand = {
        "profile": {"country": "india"},
        "skills": [{"name": f"Skill{i}"} for i in range(35)],
        "career_history": [
            {"description": "short"}
        ]
    }
    assert score_disqualifiers(cand) == 0.1

def test_score_disqualifiers_pure_research():
    # Pure research (no production keywords) = 0.5 multiplier
    cand = {
        "profile": {"country": "india"},
        "career_history": [
            {"description": "Researching transformers in academic lab."}
        ]
    }
    assert score_disqualifiers(cand) == 0.5

def test_score_behavioral_location_scoring():
    # In target city (Noida/Pune etc)
    c1 = {
        "profile": {"location": "Noida, India"},
        "redrob_signals": {"willing_to_relocate": False}
    }
    s1 = score_behavioral(c1)
    
    # Outside target city but willing to relocate
    c2 = {
        "profile": {"location": "Kochi, India"},
        "redrob_signals": {"willing_to_relocate": True}
    }
    s2 = score_behavioral(c2)
    assert s1 > s2

def test_score_behavioral_recency():
    c1 = {"redrob_signals": {"last_active_date": "2026-06-01"}} # active
    c2 = {"redrob_signals": {"last_active_date": "2025-01-01"}} # inactive
    assert score_behavioral(c1) > score_behavioral(c2)

def test_score_behavioral_notice_period():
    c1 = {"redrob_signals": {"notice_period_days": 15}} # short notice
    c2 = {"redrob_signals": {"notice_period_days": 120}} # long notice
    assert score_behavioral(c1) > score_behavioral(c2)

def test_score_candidate_disqualified():
    cand = {"profile": {"country": "US"}}
    score, breakdown = score_candidate(cand)
    assert score == 0.0
    assert breakdown.get("disqualified") is True

def test_score_candidate_success():
    cand = {
        "candidate_id": "CAND_0000001",
        "profile": {
            "country": "india",
            "location": "Pune, India",
            "years_of_experience": 6,
            "current_title": "AI Engineer",
            "summary": "shipped production AI pipelines"
        },
        "skills": [
            {"name": "FAISS", "proficiency": "expert"},
            {"name": "Python", "proficiency": "advanced"}
        ],
        "career_history": [
            {"company": "Zomato", "duration_months": 72, "description": "Built a RAG-based ranking pipeline serving 50M+ qu"}
        ],
        "redrob_signals": {
            "last_active_date": "2026-06-01",
            "open_to_work_flag": True,
            "notice_period_days": 30
        }
    }
    score, breakdown = score_candidate(cand)
    assert score > 0.0
    assert "skill" in breakdown
    assert "career" in breakdown
    assert "behavioral" in breakdown
