from app.utils.constants import (
    MUST_HAVE_SKILLS, NICE_TO_HAVE_SKILLS, DISQUALIFIER_TITLES,
    CONSULTING_FIRMS, PREFERRED_LOCATIONS_INDIA, PRODUCT_COMPANY_SIGNALS,
    JD_TARGET_CITIES
)
from app.utils.helpers import (
    days_since, text_lower, skill_map,
    proficiency_with_endorsements, education_tier_score,
    career_text, full_text
)
from app.services.honeypot import detect_honeypot

def score_skills(candidate):
    """Score: 0–1 for skill fit."""
    smap = skill_map(candidate)
    full = full_text(candidate)
    sig = candidate.get("redrob_signals", {})
    assessment_scores = sig.get("skill_assessment_scores") or {}

    must_score = 0.0
    must_hits = set()
    for keyword in MUST_HAVE_SKILLS:
        if keyword in full and keyword not in must_hits:
            must_hits.add(keyword)
            matched_skill = next((v for k, v in smap.items() if keyword in k or k in keyword), None)
            if matched_skill:
                skill_name = matched_skill.get("name", "").lower()
                prof = proficiency_with_endorsements(matched_skill)
                assess_key = next((ak for ak in assessment_scores if ak.lower() in skill_name or skill_name in ak.lower()), None)
                if assess_key:
                    assess_norm = min(assessment_scores[assess_key] / 100, 1.0)
                    prof = 0.7 * prof + 0.3 * assess_norm
                must_score += prof * 1.5
            else:
                must_score += 0.5

    nice_score = 0.0
    nice_hits = set()
    for keyword in NICE_TO_HAVE_SKILLS:
        if keyword in full and keyword not in nice_hits:
            nice_hits.add(keyword)
            matched_skill = next((v for k, v in smap.items() if keyword in k or k in keyword), None)
            if matched_skill:
                nice_score += proficiency_with_endorsements(matched_skill) * 0.5
            else:
                nice_score += 0.2

    python_skill = smap.get("python")
    python_bonus = 0.0
    if python_skill:
        python_bonus = proficiency_with_endorsements(python_skill) * 0.5

    max_must = len(MUST_HAVE_SKILLS) * 1.5
    max_nice = len(NICE_TO_HAVE_SKILLS) * 0.5
    must_norm = min(must_score / max_must, 1.0)
    nice_norm = min(nice_score / max_nice, 1.0)

    return 0.65 * must_norm + 0.25 * nice_norm + 0.10 * python_bonus

def score_career(candidate):
    """Score: 0–1 for career history fit."""
    from app.utils.constants import CAREER_TEMPLATE_WEIGHTS
    profile = candidate.get("profile", {})
    career = candidate.get("career_history", [])
    yoe = profile.get("years_of_experience", 0) or 0

    # 1. Experience range: 5–9 years ideal, 4–10 acceptable
    if 5 <= yoe <= 9:
        exp_score = 1.0
    elif 4 <= yoe < 5 or 9 < yoe <= 10:
        exp_score = 0.8
    elif 3 <= yoe < 4 or 10 < yoe <= 12:
        exp_score = 0.5
    elif yoe > 12:
        exp_score = 0.4
    else:
        exp_score = 0.1

    # 2. Exact template matching for career descriptions
    role_weights = [CAREER_TEMPLATE_WEIGHTS.get(job.get('description', '').strip()[:50], 0.0) for job in career]
    best_role_weight = max(role_weights) if role_weights else 0.0
    
    if best_role_weight == 0.0:
        return 0.0

    # 3. Product vs consulting company breakdown
    consulting_count = 0
    product_count = 0
    product_signal_count = 0
    total_jobs = max(len(career), 1)
    for job in career:
        company = (job.get("company") or "").lower()
        industry = (job.get("industry") or "").lower()
        desc = (job.get("description") or "").lower()
        if any(f in company for f in CONSULTING_FIRMS):
            consulting_count += 1
        else:
            product_count += 1
        if any(p in industry or p in desc for p in PRODUCT_COMPANY_SIGNALS):
            product_signal_count += 1
    product_score = min(product_signal_count / total_jobs, 1.0)

    # 4. Job stability — penalize < 24 months average tenure
    if career:
        tenures = [j.get("duration_months", 12) or 12 for j in career]
        avg_tenure = sum(tenures) / len(tenures)
        stability = 1.0 if avg_tenure >= 24 else (avg_tenure / 24)
    else:
        stability = 0.5

    # 5. Education tier score
    edu_score = education_tier_score(candidate)

    # Weighted career sub-score (sums to 1.0)
    score = (
        0.25 * exp_score +
        0.45 * best_role_weight +
        0.18 * stability +
        0.07 * product_score +
        0.05 * edu_score
    )
    return max(0.0, min(score, 1.0))

def score_disqualifiers(candidate):
    """Returns a multiplier: 0 = disqualified, 0.1–0.9 = penalized, 1.0 = clean."""
    profile = candidate.get("profile", {})
    career = candidate.get("career_history", [])
    full = full_text(candidate)
    
    current_title = text_lower(profile.get("current_title", ""))
    country = text_lower(profile.get("country", ""))
    
    # 1. Location check: hybrid work Noida/Pune, no visa sponsorship
    if country != "india":
        return 0.0

    # 2. Services company check: if they have ONLY worked at services companies in their career
    companies_worked = {text_lower(job.get("company", "")) for job in career if job.get("company")}
    if companies_worked:
        is_only_consulting = True
        for company in companies_worked:
            is_firm = any(f in company for f in CONSULTING_FIRMS)
            if not is_firm:
                is_only_consulting = False
                break
        if is_only_consulting:
            return 0.0

    # 3. Hard title disqualifier: clearly non-ML role with no ML career history
    for bad_title in DISQUALIFIER_TITLES:
        if bad_title in current_title:
            ml_history = any(
                any(kw in text_lower(j.get("title", "")) or kw in text_lower(j.get("description", ""))
                    for kw in ["ml", "machine learning", "ai ", "data scien", "nlp", "deep learning"])
                for j in career
            )
            if not ml_history:
                return 0.0

    # 4. Keyword stuffer penalty
    skill_count = len(candidate.get("skills", []))
    career_word_count = len(career_text(candidate).split())
    if skill_count > 30 and career_word_count < 50:
        return 0.1

    # 5. Pure research penalty
    production_signals = ["production", "deployed", "shipped", "real users", "users", "customers", "live system", "at scale"]
    has_production = any(kw in full for kw in production_signals)
    if not has_production and len(career) > 0:
        return 0.5

    return 1.0

def score_behavioral(candidate):
    """Score: 0–1 for behavioral/engagement signals."""
    sig = candidate.get("redrob_signals", {})
    profile = candidate.get("profile", {})
    
    days_inactive = days_since(sig.get("last_active_date"))
    if days_inactive < 14:
        activity_score = 1.0
    elif days_inactive < 30:
        activity_score = 0.9
    elif days_inactive < 60:
        activity_score = 0.75
    elif days_inactive < 90:
        activity_score = 0.5
    elif days_inactive < 180:
        activity_score = 0.25
    else:
        activity_score = 0.05

    open_to_work = 1.0 if sig.get("open_to_work_flag") else 0.5

    apps_30d = sig.get("applications_submitted_30d", 0) or 0
    if apps_30d >= 5:
        app_activity = 1.0
    elif apps_30d >= 2:
        app_activity = 0.7
    elif apps_30d >= 1:
        app_activity = 0.5
    else:
        app_activity = 0.3

    response_rate = sig.get("recruiter_response_rate", 0) or 0

    avg_response_hours = sig.get("avg_response_time_hours", 999) or 999
    if avg_response_hours <= 24:
        response_time_score = 1.0
    elif avg_response_hours <= 72:
        response_time_score = 0.75
    elif avg_response_hours <= 168:
        response_time_score = 0.5
    else:
        response_time_score = 0.25

    notice = sig.get("notice_period_days", 60) or 60
    if notice <= 30:
        notice_score = 1.0
    elif notice <= 60:
        notice_score = 0.7
    elif notice <= 90:
        notice_score = 0.4
    else:
        notice_score = 0.1

    icr = sig.get("interview_completion_rate", 0.5) or 0.5
    
    oar = sig.get("offer_acceptance_rate", -1)
    if oar == -1 or oar is None:
        offer_score = 0.6
    else:
        offer_score = oar

    github = sig.get("github_activity_score", -1)
    if github == -1 or github is None:
        github_score = 0.3
    else:
        github_score = min(github / 80, 1.0)

    saved = sig.get("saved_by_recruiters_30d", 0) or 0
    if saved >= 5:
        saved_score = 1.0
    elif saved >= 3:
        saved_score = 0.7
    elif saved >= 1:
        saved_score = 0.5
    else:
        saved_score = 0.3

    completeness = (sig.get("profile_completeness_score", 50) or 50) / 100

    # Location fit (within India since country outside India is disqualified)
    location = text_lower(profile.get("location", ""))
    willing_to_relocate = sig.get("willing_to_relocate", False)
    if any(city in location for city in JD_TARGET_CITIES):
        location_score = 1.0
    elif any(city in location for city in PREFERRED_LOCATIONS_INDIA):
        location_score = 0.8
    else:
        location_score = 0.65 if willing_to_relocate else 0.45

    score = (
        0.17 * activity_score +
        0.10 * open_to_work +
        0.05 * app_activity +
        0.09 * response_rate +
        0.05 * response_time_score +
        0.10 * notice_score +
        0.08 * icr +
        0.05 * offer_score +
        0.08 * github_score +
        0.05 * saved_score +
        0.08 * completeness +
        0.10 * location_score
    )
    return score

def score_candidate(candidate):
    """Master scoring function. Returns (score, breakdown_dict)."""
    # Step 1: Honeypot check
    if detect_honeypot(candidate):
        return 0.0, {"honeypot": True}
    
    # Step 2: Disqualifier check
    dq_multiplier = score_disqualifiers(candidate)
    if dq_multiplier == 0.0:
        return 0.0, {"disqualified": True}

    # Step 3: Core scores
    skill_score = score_skills(candidate)
    career_score = score_career(candidate)
    behavioral_score = score_behavioral(candidate)

    if career_score == 0.0:
        return 0.0, {"no_career_match": True}

    # Weighted composite
    composite = (
        0.45 * skill_score +
        0.35 * career_score +
        0.20 * behavioral_score
    )
    
    final = composite * dq_multiplier
    
    return round(final, 6), {
        "skill": round(skill_score, 3),
        "career": round(career_score, 3),
        "behavioral": round(behavioral_score, 3),
        "dq_mult": dq_multiplier,
    }
