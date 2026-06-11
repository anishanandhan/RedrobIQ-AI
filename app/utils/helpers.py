from datetime import datetime
from app.utils.constants import TODAY

def days_since(date_str):
    """Calculate the number of days between a candidate profile date and TODAY."""
    if not date_str:
        return 9999
    try:
        d = datetime.fromisoformat(date_str[:10])
        return (TODAY - d).days
    except Exception:
        return 9999

def text_lower(text):
    """Convert text to lowercase, safely handling None values."""
    return (text or "").lower()

def skill_names(candidate):
    """Retrieve all lowercase skill names for a candidate."""
    return [s["name"].lower() for s in candidate.get("skills", [])]

def skill_map(candidate):
    """Create a dictionary mapping lowercase skill names to their skill objects."""
    return {s["name"].lower(): s for s in candidate.get("skills", [])}

def proficiency_score(p):
    """Translate skill proficiency string into a numeric value (0 to 1.0)."""
    return {"expert": 1.0, "advanced": 0.8, "intermediate": 0.5, "beginner": 0.2}.get(
        (p or "").lower(), 0.3)

def proficiency_with_endorsements(skill_obj):
    """
    Blend declared proficiency with endorsement evidence.
    High endorsements can boost; zero endorsements on claimed expert = slight penalty.
    """
    base = proficiency_score(skill_obj.get("proficiency"))
    endorsements = skill_obj.get("endorsements") or 0
    duration = skill_obj.get("duration_months") or 0
    
    if endorsements >= 50:
        endorse_adj = 0.10
    elif endorsements >= 20:
        endorse_adj = 0.05
    elif endorsements == 0 and base >= 0.8 and duration < 6:
        endorse_adj = -0.15
    else:
        endorse_adj = 0.0
        
    return min(max(base + endorse_adj, 0.1), 1.0)

def education_tier_score(candidate):
    """
    tier_1 = IITs, IISc, BITS Pilani, NITs top → big bonus
    tier_2 = good state/private → small bonus
    tier_3 = average → neutral
    tier_4 = below average → slight negative
    """
    education = candidate.get("education", [])
    if not education:
        return 0.5
    best_tier = "tier_4"
    tier_order = {"tier_1": 0, "tier_2": 1, "tier_3": 2, "tier_4": 3}
    for e in education:
        tier = e.get("tier", "tier_4")
        if tier_order.get(tier, 3) < tier_order.get(best_tier, 3):
            best_tier = tier
    return {"tier_1": 1.0, "tier_2": 0.75, "tier_3": 0.55, "tier_4": 0.4}.get(best_tier, 0.5)

def career_text(candidate):
    """Extract all text from career history and return it in lowercase."""
    parts = []
    for job in candidate.get("career_history", []):
        parts.append(f"{job.get('title','')} {job.get('company','')} {job.get('description','')}")
    return " ".join(parts).lower()

def summary_text(candidate):
    """Extract summary and headline text in lowercase."""
    p = candidate.get("profile", {})
    return text_lower(p.get("summary", "") + " " + p.get("headline", ""))

def full_text(candidate):
    """Concatenate summary, career, skills, and certifications into a lowercase string."""
    skills = " ".join(skill_names(candidate))
    certs = " ".join(c.get("name","") for c in candidate.get("certifications", []))
    return summary_text(candidate) + " " + career_text(candidate) + " " + skills.lower() + " " + certs.lower()
