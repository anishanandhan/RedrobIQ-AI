from app.utils.helpers import days_since, skill_map, career_text, full_text

def generate_reasoning(candidate, breakdown):
    """Generate 1-2 sentence specific reasoning for a candidate."""
    profile = candidate.get("profile", {})
    sig = candidate.get("redrob_signals", {})
    career = candidate.get("career_history", [])
    
    title = profile.get("current_title", "Unknown")
    company = profile.get("current_company", "")
    yoe = profile.get("years_of_experience", 0)
    
    full = full_text(candidate)
    smap = skill_map(candidate)
    
    highlights = []
    concerns = []
    
    # Skills highlights
    key_skills_found = [k for k in ["embedding", "vector", "faiss", "qdrant", "pinecone", 
                                     "rag", "ranking", "retrieval", "elasticsearch", "weaviate",
                                     "opensearch", "sentence-transformer", "ndcg"] 
                       if k in full]
    if key_skills_found:
        highlights.append(f"hands-on with {', '.join(key_skills_found[:3])}")
    
    # Python
    py = smap.get("python")
    if py and py.get("proficiency") in ("expert", "advanced"):
        highlights.append(f"strong Python ({py.get('proficiency')})")
    
    # Career
    if any("product" in (j.get("industry","") or "").lower() for j in career):
        highlights.append("product company background")
    
    if any(kw in career_text(candidate) for kw in ["deployed", "production", "shipped"]):
        highlights.append("production ML deployment experience")
        
    # Education
    for e in candidate.get("education", []):
        if e.get("tier") == "tier_1":
            highlights.append(f"tier-1 institution ({e.get('institution','')})")
            break

    # Verified assessments
    assessments = sig.get("skill_assessment_scores") or {}
    top_assess = [(k, v) for k, v in assessments.items() if v >= 65]
    if top_assess:
        top_assess.sort(key=lambda x: -x[1])
        highlights.append(f"verified {top_assess[0][0]} score {top_assess[0][1]:.0f}/100")
    
    # Behavioral concerns
    days_inactive = days_since(sig.get("last_active_date"))
    if days_inactive > 90:
        concerns.append(f"last active {days_inactive} days ago")
    
    notice = sig.get("notice_period_days", 60)
    if notice and notice > 60:
        concerns.append(f"{notice}-day notice period")
    
    open_to_work = sig.get("open_to_work_flag", False)
    if not open_to_work:
        concerns.append("not marked open to work")
    
    # Build sentence
    highlight_str = "; ".join(highlights[:3]) if highlights else "some relevant background"
    concern_str = ("; ".join(concerns[:2])) if concerns else None
    
    sentence1 = f"{yoe:.0f}-year {title} at {company or 'current employer'} with {highlight_str}."
    
    if concern_str:
        sentence2 = f"Concerns: {concern_str}."
        return f"{sentence1} {sentence2}"
    else:
        return sentence1
