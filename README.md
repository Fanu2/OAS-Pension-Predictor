# Old Age Security (OAS) Eligibility & Timeline Calculator

![OAS](https://img.shields.io/badge/Status-Prototype-blue)

## Overview
The **OAS Eligibility & Timeline Calculator** is a web app built with Streamlit that helps users determine their eligibility for the Old Age Security (OAS) pension in Canada.  
It also visualizes the periods a user has lived in Canada after age 18 to ensure they meet the legal minimum residence requirement.

---

## Features
- **Eligibility Check:** Determines if you meet the OAS requirements based on age, citizenship/residency, and years lived in Canada.  
- **Residence Timeline:** Visualizes your time spent in Canada after age 18, helping you understand whether you meet the 10-year minimum.  
- **OAS Pension Estimate:** Estimates full or partial OAS pension based on your years of residence.

---

## How to Use
1. Enter your **year of birth**.  
2. Select your **citizenship or residency status**.  
3. Input the **periods you lived in Canada after age 18** in the format `YYYY-YYYY`, one per line.  
4. The app will display:
   - Eligibility result
   - Reasons if not eligible
   - Visual timeline of residence
   - Estimated OAS pension amount (simplified)

---

## Installation (Optional for Local Use)
```bash
git clone <repo-url>
cd <repo-folder>
pip install -r requirements.txt
streamlit run oas_eligibility_app.py
