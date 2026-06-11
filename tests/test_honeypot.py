from app.services.honeypot import detect_honeypot

def test_detect_honeypot_clean():
    # A valid candidate with normal details
    cand = {
        "profile": {"years_of_experience": 5},
        "career_history": [
            {"duration_months": 24, "start_date": "2020-01-01", "end_date": "2022-01-01"},
            {"duration_months": 36, "start_date": "2022-01-01", "end_date": "2025-01-01"}
        ],
        "skills": [
            {"name": "Python", "proficiency": "expert", "duration_months": 48}
        ]
    }
    assert detect_honeypot(cand) is False

def test_detect_honeypot_job_exceeds_yoe():
    # Rule 1: Single job duration (72m = 6y) exceeds total experience (4y) + 6 months
    cand = {
        "profile": {"years_of_experience": 4},
        "career_history": [
            {"duration_months": 72}
        ]
    }
    assert detect_honeypot(cand) is True

def test_detect_honeypot_start_after_end():
    # Rule 2: Start date after end date
    cand = {
        "profile": {"years_of_experience": 5},
        "career_history": [
            {"start_date": "2025-01-01", "end_date": "2022-01-01", "duration_months": 12}
        ]
    }
    assert detect_honeypot(cand) is True

def test_detect_honeypot_skill_exceeds_yoe():
    # Rule 3: Skill duration (84m = 7y) exceeds total experience (4y) + 12 months (5y)
    cand = {
        "profile": {"years_of_experience": 4},
        "skills": [
            {"name": "Python", "duration_months": 84}
        ]
    }
    assert detect_honeypot(cand) is True

def test_detect_honeypot_expert_zero_duration():
    # Rule 4: Expert/advanced skills with 0 duration count >= 3
    cand = {
        "profile": {"years_of_experience": 5},
        "skills": [
            {"name": "Python", "proficiency": "expert", "duration_months": 0},
            {"name": "Java", "proficiency": "advanced", "duration_months": 0},
            {"name": "Docker", "proficiency": "expert", "duration_months": 0}
        ]
    }
    assert detect_honeypot(cand) is True

def test_detect_honeypot_expert_zero_duration_less_than_3():
    # Expert/advanced with 0 duration count < 3 (only 2 here)
    cand = {
        "profile": {"years_of_experience": 5},
        "skills": [
            {"name": "Python", "proficiency": "expert", "duration_months": 0},
            {"name": "Java", "proficiency": "advanced", "duration_months": 0},
            {"name": "Docker", "proficiency": "intermediate", "duration_months": 0}
        ]
    }
    assert detect_honeypot(cand) is False

def test_detect_honeypot_yoe_mismatch():
    # Rule 5: YoE (10y) vs career history duration (24m = 2y) mismatch > 4 years
    cand = {
        "profile": {"years_of_experience": 10},
        "career_history": [
            {"duration_months": 24}
        ]
    }
    assert detect_honeypot(cand) is True
