import streamlit as st
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import os

from utils import (
    calculate_bmi, age_risk, bmi_risk, genetic_risk, hormonal_risk,
    radiation_risk, symptom_risk, reproductive_risk, lifestyle_risk
)

st.set_page_config(page_title="Breast Cancer Risk System", layout="wide")

# ================= DATABASE =================
conn = sqlite3.connect("patients.db", check_same_thread=False)
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS patients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_name TEXT,
    city TEXT,
    state TEXT,
    age_group TEXT,
    height REAL,
    weight REAL,
    bmi REAL,
    family_bc TEXT,
    ovarian_bc TEXT,
    xray TEXT,
    pills TEXT,
    menopause_meds TEXT,
    lump TEXT,
    pain TEXT,
    discharge TEXT,
    early_period TEXT,
    late_menopause TEXT,
    late_pregnancy TEXT,
    lifestyle TEXT,
    risk_score REAL,
    risk_percent REAL,
    risk_level TEXT
)
""")
conn.commit()

# ================= MENU =================
menu = st.sidebar.radio("📌 Select Option", ["Risk Prediction", "Patient Dashboard"])

# =========================================================
# ================= RISK PREDICTION ========================
# =========================================================
if menu == "Risk Prediction":

    st.title("🧬 Breast Cancer Risk Prediction System")

    page = st.radio("Select Page", ["Page 1: Basic Info", "Page 2: Health Info"])

    # ---------------- PAGE 1 ----------------
    if page == "Page 1: Basic Info":

        st.header("👩 Basic Information")

        patient_name = st.text_input("Patient Full Name")
        city = st.text_input("City / Village")
        state = st.text_input("State")

        age_group = st.selectbox("Age Group", ["<30", "30-40", "41-50", ">50"])
        height = st.number_input("Height (cm)", min_value=100.0, max_value=250.0)
        weight = st.number_input("Weight (kg)", min_value=20.0, max_value=200.0)

        family_bc = st.selectbox("Family history of breast cancer?", ["Yes", "No", "Don't Know"])
        ovarian_bc = st.selectbox("Family history of ovarian cancer?", ["Yes", "No", "Don't Know"])
        xray = st.selectbox("X-ray / Scan exposure?", ["Many times", "Few times", "Never", "Don't Know"])

        bmi = calculate_bmi(weight, height)
        st.info(f"⚖️ BMI = {round(bmi,2)}")

        st.session_state["page1"] = {
            "patient_name": patient_name,
            "city": city,
            "state": state,
            "age_group": age_group,
            "height": height,
            "weight": weight,
            "bmi": bmi,
            "family_bc": family_bc,
            "ovarian_bc": ovarian_bc,
            "xray": xray
        }

        st.success("Go to Page 2 👉")

    # ---------------- PAGE 2 ----------------
    if page == "Page 2: Health Info":

        if "page1" not in st.session_state:
            st.warning("⚠️ Please complete Page 1 first!")
        else:

            st.header("🩺 Health Information")

            pills = st.selectbox("Birth control pills?", ["No", "Short time", "Long time", "Don't Know"])
            menopause_meds = st.selectbox("Medicines after menopause?", ["No", "Short time", "Long time", "Don't Know"])

            lump = st.selectbox("Any lump in breast?", ["No", "Yes", "Don't Know"])
            pain = st.selectbox("Breast pain?", ["No", "Yes"])
            discharge = st.selectbox("Any discharge?", ["No", "Yes", "Don't Know"])

            early_period = st.selectbox("Early menstruation (<12)?", ["No", "Yes"])
            late_menopause = st.selectbox("Late menopause (>55)?", ["No", "Yes"])
            late_pregnancy = st.selectbox("First pregnancy after 30?", ["No", "Yes", "Not Applicable"])

            lifestyle = st.selectbox("Smoking / Alcohol?", ["No", "Yes"])

            if st.button("🔍 Predict Risk"):

                p1 = st.session_state["page1"]

                bmi = p1["bmi"]

                age_score = age_risk(p1["age_group"])
                bmi_score = bmi_risk(bmi)
                g_risk = genetic_risk(p1["family_bc"], p1["ovarian_bc"])
                h_risk = hormonal_risk(pills, menopause_meds)
                r_risk = radiation_risk(p1["xray"])
                symptom_score = symptom_risk(lump, pain, discharge)
                rep_risk = reproductive_risk(early_period, late_menopause, late_pregnancy)
                life_risk = lifestyle_risk(lifestyle)

                final_score = age_score + bmi_score + g_risk + h_risk + r_risk + symptom_score + rep_risk + life_risk
                max_score = 25
                risk_percent = round((final_score / max_score) * 100, 2)

                if final_score <= 6:
                    risk_level = "Low Risk"
                elif final_score <= 14:
                    risk_level = "Medium Risk"
                else:
                    risk_level = "High Risk"

                st.subheader("🧬 Final Risk Assessment")

                st.write("📊 Risk Score:", round(final_score, 2))
                st.write("📈 Risk Percentage:", risk_percent, "%")
                st.write("⚖️ BMI:", round(bmi,2))
                st.success(f"Result: {risk_level}")

                # ================= SAVE TO DATABASE =================
                c.execute("""
                INSERT INTO patients (
                    patient_name, city, state, age_group, height, weight, bmi,
                    family_bc, ovarian_bc, xray,
                    pills, menopause_meds, lump, pain, discharge,
                    early_period, late_menopause, late_pregnancy, lifestyle,
                    risk_score, risk_percent, risk_level
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    p1["patient_name"], p1["city"], p1["state"],
                    p1["age_group"], p1["height"], p1["weight"], bmi,
                    p1["family_bc"], p1["ovarian_bc"], p1["xray"],
                    pills, menopause_meds, lump, pain, discharge,
                    early_period, late_menopause, late_pregnancy, lifestyle,
                    final_score, risk_percent, risk_level
                ))
                conn.commit()
                st.success("💾 Patient data saved successfully!")

                # ================= SAVE TO CSV =================
                file_path = "patients_data.csv"

                new_data = pd.DataFrame([{
                    "patient_name": p1["patient_name"],
                    "city": p1["city"],
                    "state": p1["state"],
                    "age_group": p1["age_group"],
                    "height": p1["height"],
                    "weight": p1["weight"],
                    "bmi": bmi,
                    "risk_score": final_score,
                    "risk_percent": risk_percent,
                    "risk_level": risk_level
                }])

                if os.path.exists(file_path):
                    new_data.to_csv(file_path, mode="a", header=False, index=False)
                else:
                    new_data.to_csv(file_path, index=False)

                st.success("📁 Data also saved to CSV successfully!")

                # ================= CHART =================
                st.subheader("📊 Risk Factor Contribution")

                chart_data = {
                    "Age": age_score,
                    "BMI": bmi_score,
                    "Genetic": g_risk,
                    "Hormonal": h_risk,
                    "Radiation": r_risk,
                    "Symptoms": symptom_score,
                    "Reproductive": rep_risk,
                    "Lifestyle": life_risk
                }

                fig, ax = plt.subplots()
                ax.bar(chart_data.keys(), chart_data.values())
                plt.xticks(rotation=30)
                st.pyplot(fig)

                # ================= REPORT =================
                st.subheader("🖨 Patient Report")

                report = f"""
BREAST CANCER RISK ASSESSMENT REPORT
-------------------------------------

Patient Name: {p1['patient_name']}
City: {p1['city']}
State: {p1['state']}

Age Group: {p1['age_group']}
BMI: {round(bmi,2)}

Final Risk Score: {round(final_score,2)}
Risk Percentage: {risk_percent}%
Risk Level: {risk_level}
"""

                st.text_area("Report Preview", report, height=250)

                st.download_button(
                    "📥 Download Report",
                    report,
                    file_name=f"{p1['patient_name']}_report.txt"
                )

# =========================================================
# ================= DASHBOARD =============================
# =========================================================
if menu == "Patient Dashboard":

    st.title("📊 Patient Risk Dashboard")

    df = pd.read_sql_query("SELECT * FROM patients", conn)

    if df.empty:
        st.warning("No patient data found!")
    else:
        st.dataframe(df)

        st.subheader("📊 Risk Distribution")

        risk_counts = df["risk_level"].value_counts()

        fig, ax = plt.subplots()
        ax.bar(risk_counts.index, risk_counts.values)
        st.pyplot(fig)

        #How to Run:python -m streamlit run app3.py
