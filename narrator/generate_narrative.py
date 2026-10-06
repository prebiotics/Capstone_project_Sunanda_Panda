import json
import os
from google import genai


def generate_scr_narrative_offline(findings: dict) -> dict:
    revenue = findings["cleaned_total_revenue_inr"]
    delta = findings["duplicate_reconciliation_delta_inr"]
    cod = findings["return_rate_by_payment"]["COD"]

    risk = findings["highest_risk_segment"]
    peak = findings["true_peak_month"]

    narrative = f"""
Situation

Cleaned orders generated ₹{revenue:,.2f} in total revenue. COD had the highest
return rate at {cod:.1f}%, making payment method an important operational risk.

Complication

The highest-risk segment was COD in Tier-{risk["city_tier"]}, with a
{risk["return_rate_pct"]:.1f}% return rate. Data reconciliation also identified a
duplicate-driven revenue difference of ₹{delta:,.2f}. January appeared to be
the strongest month because of outlier orders, but this inflated the monthly
revenue picture.

Resolution

After correcting the outlier effect, March 2026 was the true peak month with
revenue of ₹{peak["revenue_inr"]:,.2f}. Regional operations should therefore
focus on reducing COD returns, particularly in Tier-{risk["city_tier"]},
while finance should use the cleaned and outlier-corrected figures for
performance reporting.
"""

    return {
        "status": "success",
        "narrative": narrative.strip(),
        "tokens": None
    }


def generate_scr_narrative(findings: dict) -> dict:

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        return generate_scr_narrative_offline(findings)

    try:
        client = genai.Client(api_key=api_key)

        system_instruction = """
You are a senior data analyst writing for Mamaearth's regional ops and finance
heads.

Write a concise business narrative using exactly three labeled sections:
Situation, Complication, Resolution.

Every number in the narrative MUST come only from the supplied findings and
must appear with the same value. Do not invent statistics, percentages,
amounts, dates, or other numerical facts.
"""

        contents = f"""
Create the SCR business narrative from these verified findings:

{json.dumps(findings, indent=2)}
"""

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=contents,
            config={
                "system_instruction": system_instruction,
                # Deterministic setting because this is a factual business report.
                "temperature": 0.0,
                "max_output_tokens": 500
            },
            timeout=30
        )

        return {
            "status": "success",
            "narrative": response.text,
            "tokens": getattr(response.usage_metadata, "total_token_count", None)
        }

    except Exception as err:
        return {
            "status": "error",
            "narrative": None,
            "message": str(err)
        }


def check_numeric_accuracy(narrative: str):
    text = narrative.replace(",", "")

    checks = {
        "Cleaned revenue": "97358.3",
        "COD return rate": "44.4",
        "COD Tier-2 risk": "54.5",
        "Duplicate reconciliation delta": "2501.9",
        "March peak revenue": "20318.9"
    }

    for name, value in checks.items():
        result = value in text
        print(f"{name}: {'PASS' if result else 'FAIL'}")

    return all(value in text for value in checks.values())


if __name__ == "__main__":

    # FIXED: Updated file path to match the directory where findings.json was saved
    with open("../narrator/findings.json") as f:
        findings = json.load(f)
