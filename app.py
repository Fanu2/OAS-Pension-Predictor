import streamlit as st
from datetime import date
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="OAS Eligibility Calculator", page_icon="👵")

st.title("Old Age Security (OAS) Eligibility & Timeline")
st.write("""
Check your eligibility for OAS in Canada and visualize your residence history after age 18.
""")

# --- User Inputs ---
birth_year = st.number_input("Enter your year of birth:", min_value=1900, max_value=date.today().year, value=1958)
citizenship = st.selectbox("Are you a Canadian citizen or legal resident?", ["Yes", "No"])

st.write("Enter the periods you lived in Canada after age 18:")
residency_periods_input = st.text_area("""
Enter each period as `YYYY-YYYY`, one per line.
Example:
1980-1990
1992-2023
""", height=150)

# --- Calculate Age ---
current_year = date.today().year
age = current_year - birth_year

# --- Process Residency Periods ---
def parse_periods(periods_text):
    periods = []
    for line in periods_text.strip().split("\n"):
        if "-" in line:
            start, end = line.split("-")
            try:
                start, end = int(start), int(end)
                periods.append((start, end))
            except:
                pass
    return periods

residency_periods = parse_periods(residency_periods_input)
total_years = sum(end - start for start, end in residency_periods)

# --- Eligibility Logic ---
eligible = age >= 65 and citizenship == "Yes" and total_years >= 10
reasons = []

if age < 65:
    reasons.append("You must be at least 65 years old.")
if citizenship != "Yes":
    reasons.append("You must be a Canadian citizen or legal resident.")
if total_years < 10:
    reasons.append(f"You must have lived in Canada for at least 10 years after age 18. You entered {total_years} years.")

# --- Display Result ---
st.write("---")
st.subheader("Eligibility Result:")
if eligible:
    st.success("✅ You are eligible for OAS")
else:
    st.error("❌ You are not eligible for OAS")
for r in reasons:
    st.info(r)

# --- Timeline Visualization ---
if residency_periods:
    st.write("---")
    st.subheader("Residence Timeline After Age 18")

    df = pd.DataFrame(residency_periods, columns=["Start Year", "End Year"])
    df["Duration"] = df["End Year"] - df["Start Year"]

    fig, ax = plt.subplots(figsize=(10, 2))
    for i, row in df.iterrows():
        ax.barh(0, row["Duration"], left=row["Start Year"], color="skyblue", edgecolor="black")
        ax.text(row["Start Year"] + row["Duration"]/2, 0, f"{row['Start Year']}-{row['End Year']}", 
                ha="center", va="center", color="black", fontsize=9)

    ax.set_yticks([])
    ax.set_xlabel("Year")
    ax.set_title("Timeline of Years Lived in Canada After Age 18")
    ax.set_xlim(min([s for s, e in residency_periods])-1, max([e for s, e in residency_periods])+1)
    st.pyplot(fig)

# --- Optional: Estimate OAS Amount ---
st.write("---")
st.subheader("Estimated OAS Pension Amount (Simplified)")
if total_years >= 40:
    st.write("💰 Full OAS pension (based on 40+ years of residence)")
else:
    percentage = int((total_years / 40) * 100)
    st.write(f"💰 Partial OAS pension (~{percentage}% of full amount) based on {total_years} years of residence")

st.write("""
---
*This tool provides a basic estimate. For official determination and exact amounts, consult [Government of Canada OAS](https://www.canada.ca/en/services/benefits/publicpensions/cpp/old-age-security.html).*
""")
