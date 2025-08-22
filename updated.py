import streamlit as st
from datetime import date, timedelta
import pandas as pd
import plotly.express as px

# Page configuration
st.set_page_config(page_title="OAS Eligibility Calculator", page_icon="👵", layout="wide")
st.title("🇨🇦 Enhanced OAS Eligibility Calculator")
st.write("""
This tool helps estimate eligibility for Old Age Security (OAS) pension based on residency requirements.
**Note:** This is an estimation tool only. Always verify with [Service Canada](https://www.canada.ca/en/services/benefits/publicpensions/cpp/old-age-security/eligibility.html) for official determination.
""")

# Sidebar with information
with st.sidebar:
    st.header("About OAS Eligibility")
    st.info("""
    **Official OAS Residency Requirements:**
    - Must be 65 years or older
    - Must be a Canadian citizen or legal resident at time of application
    - Must have resided in Canada for at least 10 years after turning 18
    - For full pension: 40 years of residence after age 18
    """)
    st.warning("""
    **Important Notes:**
    - Some absences may be counted under certain conditions
    - International social security agreements may affect eligibility
    - Always consult with Service Canada for official determination
    """)
    st.markdown("[🔗 Official OAS Eligibility Information](https://www.canada.ca/en/services/benefits/publicpensions/cpp/old-age-security/eligibility.html)")

# Initialize session state
if "residency_periods" not in st.session_state:
    st.session_state.residency_periods = []

# Main calculator
col1, col2 = st.columns([2, 1])

with col1:
    st.header("Residence History")
    
    min_date = date(1950, 1, 1)  # Reasonable minimum date for residency tracking
    max_date = date.today()
    
    # Date input section
    with st.expander("Add Residence Period", expanded=True):
        from_date = st.date_input("From Date:", min_value=min_date, max_value=max_date, key="from_date")
        to_date = st.date_input("To Date:", min_value=min_date, max_value=max_date, key="to_date")
        
        # Validate date range
        if from_date and to_date:
            if to_date < from_date:
                st.error("End date must be after start date.")
            else:
                days_in_period = (to_date - from_date).days + 1
                st.write(f"Days in this period: {days_in_period}")
                
                if st.button("Add This Period", key="add_period"):
                    # Check for overlaps
                    overlap = False
                    for period in st.session_state.residency_periods:
                        if not (to_date < period['from_date'] or from_date > period['to_date']):
                            overlap = True
                            break
                    
                    if overlap:
                        st.error("This period overlaps with an existing period. Please adjust.")
                    else:
                        st.session_state.residency_periods.append({
                            'from_date': from_date,
                            'to_date': to_date,
                            'days': days_in_period
                        })
                        st.success("Period added successfully!")
    
    # Display and manage periods
    if st.session_state.residency_periods:
        st.subheader("Your Residence Periods")
        total_days = 0
        
        # Create dataframe for display
        period_data = []
        for i, period in enumerate(st.session_state.residency_periods):
            period_data.append({
                "Period": i+1,
                "From": period['from_date'],
                "To": period['to_date'],
                "Days": period['days']
            })
            total_days += period['days']
        
        df_periods = pd.DataFrame(period_data)
        st.dataframe(df_periods, use_container_width=True)
        
        # Calculate years
        total_years = total_days / 365.25
        st.metric("Total Residence Days", f"{total_days:,}")
        st.metric("Total Residence Years", f"{total_years:.2f}")
        
        # Remove button
        if st.button("Clear All Periods", type="secondary"):
            st.session_state.residency_periods = []
            st.rerun()

with col2:
    st.header("Eligibility Assessment")
    
    # Personal information
    st.subheader("Your Information")
    birth_date = st.date_input("Your Date of Birth:", 
                              min_value=date(1900, 1, 1), 
                              max_value=date.today())
    
    # Calculate age
    if birth_date:
        today = date.today()
        age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
        st.write(f"Current age: {age}")
    
    citizenship = st.radio(
        "Citizenship/Legal Status:",
        ["Canadian Citizen", "Legal Resident", "Neither"],
        help="You must be a Canadian citizen or legal resident at the time of application"
    )
    
    # Eligibility calculation
    if st.session_state.residency_periods and birth_date:
        # Basic eligibility
        meets_age = age >= 65
        meets_status = citizenship in ["Canadian Citizen", "Legal Resident"]
        meets_residency = total_days >= 3650  # 10 years
        
        # Detailed residency calculation (after age 18)
        age_18_date = birth_date + timedelta(days=365.25*18)
        eligible_days = 0
        
        for period in st.session_state.residency_periods:
            # Only count days after turning 18
            period_start = max(period['from_date'], age_18_date)
            period_end = period['to_date']
            
            if period_start <= period_end:
                eligible_days += (period_end - period_start).days + 1
        
        # Check eligibility
        eligible = meets_age and meets_status and eligible_days >= 3650
        
        # Display results
        st.subheader("Eligibility Results")
        
        if eligible:
            st.success("**Preliminary Assessment: Likely Eligible**")
            
            # Determine pension amount
            if eligible_days >= 14610:  # 40 years
                st.info("You appear to qualify for the **full OAS pension**")
            else:
                partial_percentage = (eligible_days / 14610) * 100
                st.info(f"You appear to qualify for a **partial OAS pension** ({partial_percentage:.1f}% of full amount)")
        else:
            st.error("**Preliminary Assessment: Not Currently Eligible**")
            
            # Explain why
            reasons = []
            if not meets_age:
                reasons.append(f"- You are {age} years old but must be 65 or older")
            if not meets_status:
                reasons.append("- You must be a Canadian citizen or legal resident")
            if eligible_days < 3650:
                years_short = (3650 - eligible_days) / 365.25
                reasons.append(f"- You have {eligible_days} days of eligible residency but need 3,650 (approximately {years_short:.1f} more years)")
            
            st.write("**Reasons:**")
            for reason in reasons:
                st.write(reason)
        
        # Show detailed residency info
        st.write("**Residency Details:**")
        st.write(f"- Total days in Canada: {total_days}")
        st.write(f"- Eligible days (after age 18): {eligible_days}")
        st.write(f"- Equivalent years: {eligible_days/365.25:.2f}")
    
    elif not st.session_state.residency_periods:
        st.info("Add residence periods to check eligibility")
    else:
        st.info("Enter your date of birth to check eligibility")

# Additional information
st.divider()
st.header("Additional Information")

tab1, tab2, tab3 = st.tabs(["OAS Basics", "Residency Rules", "Next Steps"])

with tab1:
    st.write("""
    **Old Age Security (OAS) Pension**
    
    The OAS pension is a monthly payment available to most Canadians 65 years of age or older. 
    You must meet legal status and residence requirements.
    
    - **Full pension:** Requires 40 years of residence in Canada after age 18
    - **Partial pension:** Requires at least 10 years of residence in Canada after age 18
    - **Payment amounts:** Adjusted quarterly based on the Consumer Price Index
    """)

with tab2:
    st.write("""
    **Understanding Residency Requirements**
    
    Residence is defined as the place where you make your home and ordinarily live. 
    Some important considerations:
    
    - Time spent outside Canada may count in certain circumstances
    - Special rules apply for those who lived abroad while working for Canadian employers
    - International social security agreements may affect eligibility
    - You must be a resident of Canada on the day your application is approved
    """)
    
    st.warning("""
    **Important:** Short trips outside Canada generally count as residence, 
    but extended absences may not be counted toward the residency requirement.
    """)

with tab3:
    st.write("""
    **What to Do Next**
    
    1. **Verify your eligibility** with Service Canada for an official determination
    2. **Apply for OAS** 6 months before you turn 65
    3. **Consider applying for other benefits** like GIS if you have a low income
    4. **Contact Service Canada** if you have questions about your specific situation
    """)
    
    st.markdown("""
    **Helpful Resources:**
    - [Service Canada OAS Overview](https://www.canada.ca/en/services/benefits/publicpensions/cpp/old-age-security.html)
    - [OAS Application Process](https://www.canada.ca/en/services/benefits/publicpensions/cpp/old-age-security/apply.html)
    - [OAS Payment Rates](https://www.canada.ca/en/services/benefits/publicpensions/cpp/old-age-security/payments.html)
    """)

# Footer
st.divider()
st.caption("""
This calculator is for informational purposes only. Eligibility for OAS benefits is determined solely by Service Canada 
based on complete assessment of your individual circumstances. Always consult official government sources for accurate information.
""")
