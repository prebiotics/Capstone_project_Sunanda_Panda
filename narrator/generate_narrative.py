# ============================================================
# TASK 2: Generate the SCR narrative using Gemini
# ============================================================

import json
import os
from pathlib import Path
from google import genai
from google.genai import types


def generate_scr_narrative(findings: dict) -> dict:

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        return generate_scr_narrative_offline(findings)

    # ============================================================
    # TASK 3: Lock parameters and handle API errors
    # ============================================================

    try:
        client = genai.Client(
            api_key=api_key,
            http_options=types.HttpOptions(timeout=30000)
        )

        system_instruction = """
        You are a senior data analyst writing for Mamaearth's
        regional ops and finance heads.

        Write exactly three labeled sections:
        Situation, Complication, and Resolution.

        Every number must come from the supplied findings and retain
        the same value. Do not invent statistics.
        """

        contents = f"""
        Write a business narrative using these verified findings:

        {json.dumps(findings, indent=2)}
        """

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                # Temperature 0 is suitable for factual reporting.
                temperature=0.0,
                max_output_tokens=500
            )
        )

        if not response.text:
            raise ValueError("Gemini returned an empty narrative.")

        usage = getattr(response, "usage_metadata", None)

        return {
            "status": "success",
            "narrative": response.text,
            "tokens": getattr(usage, "total_token_count", None)
        }

    except Exception as err:
        return {
            "status": "error",
            "narrative": None,
            "message": str(err)
        }


# ============================================================
# TASK 4: Generate an offline SCR narrative without an API key
# ============================================================

def generate_scr_narrative_offline(findings: dict) -> dict:

    revenue = findings["cleaned_total_revenue_inr"]
    delta = findings["duplicate_reconciliation_delta_inr"]
    rates = findings["return_rate_by_payment"]
    risk = findings["highest_risk_segment"]
    peak = findings["true_peak_month"]
    january = findings["outlier_inflated_month"]

    narrative = f"""
Situation

Cleaned total revenue was ₹{revenue:,.2f}. Return rates were
{rates["COD"]:.1f}% for COD, {rates["CARD"]:.1f}% for CARD,
and {rates["UPI"]:.1f}% for UPI.

Complication

The highest-risk segment was {risk["payment_method"]} in
Tier-{risk["city_tier"]}, with a return rate of
{risk["return_rate_pct"]:.1f}%. The duplicate-driven reconciliation
difference was ₹{delta:,.2f}. January 2026 revenue appeared to be
₹{january["apparent_revenue_inr"]:,.2f}, but after outlier correction
it was ₹{january["corrected_revenue_inr"]:,.2f}.

Resolution

After correcting for outliers, {peak["month"]} was the true peak month,
with revenue of ₹{peak["revenue_inr"]:,.2f}. Operations should focus
on reducing COD returns, particularly in Tier-{risk["city_tier"]},
while finance should use reconciled revenue figures.
"""

    return {
        "status": "success",
        "narrative": narrative.strip(),
        "tokens": None
    }


# ============================================================
# TASK 5: Check the five required figures and save sample output
# ============================================================

def check_numeric_accuracy(narrative: str) -> bool:

    text = narrative.replace(",", "").lower()

    checks = [
        ("Cleaned revenue", ["97358.30"]),
        ("COD return rate", ["44.4"]),
        ("COD Tier-2 risk", ["54.5"]),
        ("Reconciliation delta", ["2501.90"]),
        ("March peak revenue", ["march", "20318.90"])
    ]

    all_passed = True

    for name, values in checks:
        passed = all(value in text for value in values)
        print(f"{name}: {'PASS' if passed else 'FAIL'}")
        if not passed:
            all_passed = False

    return all_passed


# ============================================================
# RUN TASKS 2-5
# ============================================================

if __name__ == "__main__":

    folder = Path(__file__).resolve().parent

    with open(folder / "findings.json", encoding="utf-8") as f:
        findings = json.load(f)

    # Use Gemini when a key exists; otherwise use the offline function.
    result = generate_scr_narrative(findings)

    # If Gemini fails, switch to the offline fallback.
    if result["status"] == "error":
        print("Gemini failed; using offline fallback.")
        print(result["message"])
        result = generate_scr_narrative_offline(findings)

    print("\n--- SCR NARRATIVE ---\n")
    print(result["narrative"])

    # Save the actual generated narrative.
    output_path = folder / "sample_output.txt"
    output_path.write_text(result["narrative"], encoding="utf-8")

    # Check the saved sample output.
    saved_narrative = output_path.read_text(encoding="utf-8")

    print("\n--- NUMERIC ACCURACY CHECK ---")
    if not check_numeric_accuracy(saved_narrative):
        raise AssertionError("Numeric accuracy check failed.")

    print("\nSample output saved successfully.")
