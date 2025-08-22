# Old Age Security (OAS) Eligibility Calculator

This is a Streamlit web app to help Canadian residents calculate their eligibility for **Old Age Security (OAS)** based on their residence history after 2010. It provides an **interactive timeline**, displays **eligible days per period**, and calculates **total eligible days** for OAS.

---

## Features

- **Add multiple residence periods** with **From** and **To** dates.  
- **Non-overlapping validation** ensures periods do not conflict.  
- **Display eligible days per period** and **total eligible days**.  
- **Remove periods** safely at any time.  
- **Interactive timeline** visualizing:
  - Green bars → periods counting toward OAS  
  - Red bars → gaps between residence periods  
- **Eligibility check** based on age, citizenship, and total residence days.  
- **Partial OAS calculation** (approximate based on residence days).

---

## How to Use

1. Select your **birth year** and indicate if you are a **Canadian citizen or legal resident**.  
2. Add residence periods using the **From** and **To** date pickers (from 2010 onwards).  
3. Ensure periods **do not overlap**.  
4. View the **table of periods** showing eligible days and the **total days**.  
5. Check the **interactive timeline** to visualize
