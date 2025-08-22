import streamlit as st
from datetime import date
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="OAS Eligibility Calculator", page_icon="👵")
st.title("OAS Eligibility & Timeline with Multiple Periods")
st.write("Visualize your residence history after age 18 with gaps, eligible days, and total days for OAS.")

# --- User Inputs ---
birth_year = st.number_input("Enter your year of birth:", min_value=1900, max_value=date.today().year, value=1958)
citizenship = st.selectbox("Are you a Canadian citizen or legal resident?", ["Yes", "No"])

# --- Initialize session state for periods ---
if "residency_periods" not in st.session_state:
    st.session_state.residency_periods = []

st.write("Add periods you lived in Canada after age 18:")

# --- Date Picker Form ---
with st.form(key="residency_form"):
    start_date = st.date_input("From:", min_value=date(birth_year+18,1,1), max_value=date.today())
    end_date = st.date_input("To:", min_value=start_date, max_value=date.today())
    add_period = st.form_submit_button("Add Period")
    if add_period:
        st.session_state.residency_periods.append((start_date, end_date))

# --- Display periods with eligible days & remove buttons ---
if st.session_state.residency_periods:
    st.write("### Residence Periods Entered")
    table_data = []
    for idx, (s, e) in enumerate(st.session_state.residency_periods):
        days = (e - s).days
        table_data.append({"From": s, "To": e, "Eligible Days": days})
        col1, col2 = st.columns([8,1])
        col1.write(f"{idx+1}. {s} → {e} | Eligible Days: {days}")
        if col2.button("Remove", key=f"remove_{idx}"):
            st.session_state.residency_periods.pop(idx)
            st.experimental_rerun()

    df_table = pd.DataFrame(table_data)
    total_days = df_table["Eligible Days"].sum()
    st.write(f"**Total Eligible Days:** {total_days} days")
else:
    total_days = 0

# --- Calculate Age ---
current_year = date.today().year
age = current_year - birth_year

# --- Eligibility Logic ---
eligible = age >= 65 and citizenship == "Yes" and total_days >= 3650  # 10 years ≈ 3650 days
reasons = []
if age < 65:
    reasons.append("You must be at least 65 years old.")
if citizenship != "Yes":
    reasons.append("You must be a Canadian citizen or legal resident.")
if total_days < 3650:
    reasons.append(f"You must have lived in Canada for at least 10 years (3650 days) after age 18. You entered {total_days} days.")

# --- Display Result ---
st.write("---")
st.subheader("Eligibility Result:")
if eligible:
    st.success("✅ You are eligible for OAS")
else:
    st.error("❌ You are not eligible for OAS")
for r in reasons:
    st.info(r)

# --- Prepare Timeline Data ---
timeline_data = []
periods = sorted(st.session_state.residency_periods, key=lambda x: x[0])

# Green periods (residency)
for s, e in periods:
    timeline_data.append({
        "Start": s,
        "End": e,
        "Label": f"{s} → {e}",
        "Days": (e - s).days,
        "Color": "green"
    })

# Red gaps
for i in range(1, len(periods)):
    prev_end = periods[i-1][1]
    curr_start = periods[i][0]
    if curr_start > prev_end:
        timeline_data.append({
            "Start": prev_end,
            "End": curr_start,
            "Label": f"Gap: {prev_end} → {curr_start}",
            "Days": (curr_start - prev_end).days,
            "Color": "red"
        })

df = pd.DataFrame(timeline_data)

# --- Interactive Timeline ---
if not df.empty:
    st.write("---")
    st.subheader("Interactive Timeline with Gaps")
    fig = px.timeline(df, x_start="Start", x_end="End", y=["Label"]*len(df),
                      hover_data={"Start": True, "End": True, "Days": True, "Label": False},
                      color="Color", color_discrete_map={"green":"green","red":"red"})
    fig.update_yaxes(showticklabels=False)
    fig.update_layout(height=200 + 40*len(df), title="Timeline of Residence (Green=Counted, Red=Gap)")
    st.plotly_chart(fig, use_container_width=True)

# --- OAS Pension Estimate ---
st.write("---")
st.subheader("Estimated OAS Pension Amount (Simplified)")
full_pension_days = 40*365  # 40 years ≈ 14600 days
if total_days >= full_pension_days:
    st.write("💰 Full OAS pension (based on 40+ years of residence)")
else:
    percentage = int((total_days/full_pension_days)*100)
    st.write(f"💰 Partial OAS pension (~{percentage}% of full amount) based on {total_days} days of residence")

st.write("""
---
*This tool provides a basic estimate. For official determination and exact amounts, consult [Government of Canada OAS](https://www.canada.ca/en/services/benefits/publicpensions/cpp/old-age-security.html).*
""")
