from datetime import datetime

def detect_honeypot(candidate):
    """
    Returns True if candidate looks like a honeypot (impossible/faked profile).
    Checks 5 deterministic logical anomaly rules:
    1. Single job duration exceeds total YoE + 6 months.
    2. Single job start date is after the end date.
    3. Skill duration exceeds total YoE + 12 months.
    4. Expert/advanced skills with 0 duration count >= 3.
    5. YoE vs sum of career history duration mismatch > 4 years.
    """
    career = candidate.get("career_history", [])
    profile = candidate.get("profile", {})
    skills = candidate.get("skills", [])
    
    yoe = profile.get("years_of_experience", 0) or 0

    # Rule 1 & 2: Single job duration > total experience or start > end
    for job in career:
        duration = job.get("duration_months", 0) or 0
        if duration > yoe * 12 + 6:
            return True
            
        start = job.get("start_date", "")
        end = job.get("end_date", "")
        if start and end and start > end:
            return True
        if start and end:
            try:
                s = datetime.fromisoformat(start[:10])
                e = datetime.fromisoformat(end[:10])
                actual_months = (e.year - s.year) * 12 + (e.month - s.month)
                if abs(actual_months - duration) > 24:
                    return True
            except Exception:
                pass

    # Rule 3: Skill duration exceeds total experience
    for sk in skills:
        sk_dur = sk.get("duration_months", 0) or 0
        if sk_dur > yoe * 12 + 12:
            return True

    # Rule 4: Expert/advanced skills with 0 duration count >= 3
    expert_zero_dur = sum(
        1 for s in skills
        if s.get("proficiency") in ("expert", "advanced") and
        (s.get("duration_months") or 0) == 0
    )
    if expert_zero_dur >= 3:
        return True

    # Rule 5: YoE vs career history mismatch > 4 years
    if career:
        total_career_months = sum(j.get("duration_months", 0) or 0 for j in career)
        total_career_years = total_career_months / 12
        if abs(total_career_years - yoe) > 4:
            return True

    return False
