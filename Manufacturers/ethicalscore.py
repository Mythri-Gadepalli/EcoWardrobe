import pandas as pd
import re
from penalty_keywords import penalty_keywords

# Certification weights
certification_scores = {
    "GOTS": 25,
    "Fair Trade": 24,
    "FLA Accreditation": 23,
    "SA8000": 23,
    "OEKO-TEX": 23,
    "WRAP": 22,
    "BSCI": 21,
    "SEDEX": 21,
    "LABS Initiative": 21,
    "ISO 14001": 20,
    "BCI (Better Cotton)": 19,
    "ISO 45001": 19,
    "ISO 9001": 18,
    "OHSAS 18001": 18,
    "Inache (internal)": 15
}

# Base values
BASE_VALUES = {
    "fair_wages": 15,
    "worker_safety": 15,
    "child_labor": 15,
    "worker_satisfaction": 10,
    "certifications": 25,
    "working_hours": 10,
    "ethical_longevity": 10
}

# Read Excel
df = pd.read_excel("Manufacturers.xlsx")

# Score calculation functions
def keyword_match(text, keywords):
    if pd.isna(text):
        return False
    text = text.lower()
    return any(kw.lower() in text for kw in keywords)

def score_certifications(received, names, reason, years):
    if received == 0:
        if keyword_match(reason, penalty_keywords["certifications"]["high"]):
            return 0, "No certifications - High Penalty: 0"
        return (10 if years < 2 else 5), f"No certifications - {10 if years < 2 else 5} (based on company age)"
    
    if pd.isna(names):
        return 0, "Certifications received = 1 but names missing - 0"

    cert_list = [c.strip() for c in str(names).split(',')]
    highest_score = 0
    for cert in cert_list:
        score = certification_scores.get(cert, 0)
        highest_score = max(highest_score, score)
    return min(highest_score, BASE_VALUES["certifications"]), f"Certifications: {cert_list} - Score: {min(highest_score, BASE_VALUES['certifications'])}"

def score_category(boolean_val, reason, category, high_val, med_val, label):
    if boolean_val == True:
        return high_val, f"{label}: TRUE - {high_val}"
    elif keyword_match(reason, penalty_keywords[category]["high"]):
        return 0, f"{label}: FALSE - High Penalty: 0"
    else:
        return med_val, f"{label}: FALSE - {med_val} (no high-penalty keywords)"

def score_working_hours(hours):
    try:
        hours = float(hours)
    except (ValueError, TypeError):
        return 0, "Working Hours: Invalid - 0"

    if hours <= 8:
        return 10, "Working Hours <= 8 - 10"
    elif 8 < hours <= 10:
        return 5, "Working Hours 8-10 - 5"
    else:
        return 0, "Working Hours > 10 - 0"

def score_ethical_longevity(years):
    if pd.isna(years):
        return 0, "Ethical Longevity: Unknown - 0"
    if years >= 10:
        return 10, "Ethical Longevity >= 10 years - 10"
    elif years >= 5:
        return 5, "Ethical Longevity 5-9 years - 5"
    else:
        return 0, "Ethical Longevity <5 years - 0"

# Apply scoring
scores = []
for _, row in df.iterrows():
    score_fw, audit_fw = score_category(row['Is Fair Wages'], row['Reason for Unfair Wages'], 'fair_wages', 15, 7, "Fair Wages")
    score_wh, audit_wh = score_working_hours(row['Working Hours'])
    score_ws, audit_ws = score_category(row['Is Worker Safe'], row['Reason for Lack of Worker Safety'], 'worker_safety', 15, 7, "Worker Safety")
    score_cl, audit_cl = score_category(row['No Child Labor'], row['Reason for Child Labor'], 'child_labor', 15, 7, "No Child Labor")
    score_sat, audit_sat = score_category(row['Is Worker Satisfied'], row['Reason for Low Worker Satisfaction'], 'worker_satisfaction', 10, 5, "Worker Satisfaction")
    score_cert, audit_cert = score_certifications(row['Certifications Received'], row['Certification Names'], row['Reason for No Certifications'], row['Years Since Establishment'])
    score_longevity, audit_longevity = score_ethical_longevity(row['Years Since Establishment'])

    total_score = score_fw + score_wh + score_ws + score_cl + score_sat + score_cert + score_longevity
    max_possible_score = sum(BASE_VALUES.values())
    ethical_score_10 = round((total_score / max_possible_score) * 10, 1)

    if ethical_score_10 >= 8.5:
        rating = "Excellent"
    elif ethical_score_10 >= 6:
        rating = "Good"
    elif ethical_score_10 >= 4:
        rating = "Needs Improvement"
    else:
        rating = "Poor"

    audit = " | ".join([
        audit_fw,
        audit_wh,
        audit_ws,
        audit_cl,
        audit_sat,
        audit_cert,
        audit_longevity
    ])
    

    scores.append({
        "Ethical Score (1-10)": ethical_score_10,
        "Ethical Rating": rating,
        "Audit": audit
    })

# Append scores to dataframe
scores_df = pd.DataFrame(scores)
df = pd.concat([df, scores_df], axis=1)

# Save to CSV
df.to_csv("Scored.csv", index=False)
print("Scored.csv has been generated.")
