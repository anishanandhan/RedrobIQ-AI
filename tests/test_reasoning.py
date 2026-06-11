from app.services.reasoning import generate_reasoning

def test_generate_reasoning_full_highlights():
    cand = {
        "profile": {
            "years_of_experience": 7,
            "current_title": "Senior AI Engineer",
            "current_company": "Zomato",
            "summary": "shipped production AI pipelines"
        },
        "skills": [
            {"name": "FAISS", "proficiency": "expert"},
            {"name": "Python", "proficiency": "expert"}
        ],
        "education": [
            {"tier": "tier_1", "institution": "IIT Bombay"}
        ],
        "career_history": [
            {"industry": "product", "company": "Zomato", "description": "deployed ranking models"}
        ],
        "redrob_signals": {
            "skill_assessment_scores": {"FAISS": 90},
            "last_active_date": "2026-06-01",
            "open_to_work_flag": True,
            "notice_period_days": 30
        }
    }
    
    breakdown = {"skill": 0.9, "career": 0.8, "behavioral": 0.9}
    reasoning = generate_reasoning(cand, breakdown)
    
    assert "7-year Senior AI Engineer" in reasoning
    assert "Zomato" in reasoning
    assert "hands-on with faiss" in reasoning
    assert "strong Python" in reasoning
    assert "product company background" in reasoning
    assert "Concerns:" not in reasoning

def test_generate_reasoning_with_concerns():
    cand = {
        "profile": {
            "years_of_experience": 4,
            "current_title": "ML Engineer",
            "current_company": "Glance",
            "summary": "researching neural networks"
        },
        "skills": [
            {"name": "PyTorch", "proficiency": "intermediate"}
        ],
        "education": [],
        "career_history": [],
        "redrob_signals": {
            "last_active_date": "2025-01-01", # inactive
            "open_to_work_flag": False,       # not open
            "notice_period_days": 90          # long notice
        }
    }
    
    breakdown = {"skill": 0.4, "career": 0.3, "behavioral": 0.2}
    reasoning = generate_reasoning(cand, breakdown)
    
    assert "4-year ML Engineer" in reasoning
    assert "Glance" in reasoning
    assert "Concerns:" in reasoning
    # Should flag notice period or inactivity or not open
    assert "notice period" in reasoning or "not marked open to work" in reasoning or "last active" in reasoning
