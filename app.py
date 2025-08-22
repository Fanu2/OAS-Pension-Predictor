import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="OAS Eligibility Calculator", page_icon="👵")
st.title("OAS Eligibility Calculator - Year Selector")
st.write("Add multiple residence periods using From and To years (2010 onwards).")

# --- Initialize session state ---
if "residency_periods" not in st.session_state:
    st.session_state.residency_periods = []

# --- Year dropdowns ---
current_year = 2025  # or use date.today().year
years = list(range(2010, current_year + 1))

with st.form("add_period_form"):
    from_year = st.selectbox("From Year:", years, index=0)
    to_year = st.selectbox("To Year:", [y for y in years if y >= from_year], index=len(years) - 1)
    add_period = st.form_submit_button("Add Period")

    if add_period:
        # Check for overlaps
        overlap = False
        for s, e in st.session_state.residency_periods:
            if not (to_year < s or from_year > e):
                overlap = True
                break
        if overlap:
            st.error("This period overlaps with an existing period. Please select a non-overlapping period.")
        else:
            st.session_state.residency_periods.append((from_year, to_year))
            st.success(f"Added period: {from_year} → {to_year}")

# --- Display periods with eligible days & remove buttons ---
if st.session_state.residency_periods:
    st.write("### Residence Periods Entered")
    table_data = []
    for idx, (s, e) in enumerate(st.session_state.residency_periods.copy()):
        days = (e - s + 1) * 365  # Approximate days per year
        table_data.append({"From": s, "To": e, "Eligible Days": days})
        col1, col2 = st.columns([8, 1])
        col1.write(f"{idx+1}. {s} → {e} | Eligible Days: {days}")
        if col2.button("Remove", key=f"remove_{idx}"):
            st.session_state.residency_periods.pop(idx)
            st.experimental_rerun()

    df_table = pd.DataFrame(table_data)
    total_days = df_table["Eligible Days"].sum()
    st.write(f"**Total Eligible Days:** {total_days}")
else:
    total_days = 0

# --- User Inputs for Eligibility ---
birth_year = st.number_input("Enter your birth year:", min_value=1900, max_value=current_year, value=1958)
citizenship = st.selectbox("Are you a Canadian citizen or legal resident?", ["Yes", "No"])
age = current_year - birth_year

# --- Eligibility Logic ---
eligible = age >= 65 and citizenship == "Yes" and total_days >= 3650
reasons = []
if age < 65:
    reasons.append("You must be at least 65 years old.")
if citizenship != "Yes":
    reasons.append("You must be a Canadian citizen or legal resident.")
if total_days < 3650:
    reasons.append(f"You must have lived in Canada for at least 10 years (3650 days). You entered {total_days} days.")

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

# Green periods
for s, e in periods:
    timeline_data.append({
        "Start": pd.Timestamp(f"{s}-01-01"),
        "End": pd.Timestamp(f"{e}-12-31"),
        "Label": f"{s} → {e}",
        "Days": (e - s + 1) * 365,
        "Color": "green"
    })

# Red gaps
for i in range(1, len(periods)):
    prev_end = periods[i-1][1]
    curr_start = periods[i][0]
    if curr_start > prev_end + 1:
        timeline_data.append({
            "Start": pd.Timestamp(f"{prev_end+1}-01-01"),
            "End": pd.Timestamp(f"{curr_start-1}-12-31"),
            "Label": f"Gap: {prev_end+1} → {curr_start-1}",
            "Days": (curr_start - prev_end - 1) * 365,
            "Color": "red"
        })

df = pd.DataFrame(timeline_data)

# --- Interactive Timeline ---
if not df.empty:
    st.write("---")
    st.subheader("Interactive Timeline")
    fig = px.timeline(df, x_start="Start", x_end="End", y=["Label"]*len(df),
                      hover_data={"Start": True, "End": True, "Days": True, "Label": False},
                      color="Color", color_discrete_map={"green":"green","red":"red"})
    fig.update_yaxes(showticklabels=False)
    fig.update_layout(height=200 + 40*len(df))
    st.plotly_chart(fig, use_container_width=True)
