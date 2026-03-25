import streamlit as st
import joblib
import numpy as np


# ------------------------------------------------
# PHASE 6 LOGIC: Nutrition Calculator
# ------------------------------------------------
def calculate_milk_nutrition(
        fat, protein, lactose,
        infant_weight, volume_limit,
        protein_target, calorie_target):

    # STEP 1: Milk calories (kcal/dL)
    calories = (protein * 4.4) + (fat * 8.79) + (lactose * 3.87)

    # STEP 2: Delivered nutrition
    protein_delivered = (protein * volume_limit) / 100
    calorie_delivered = (calories * volume_limit) / 100

    # STEP 3: Target checks
    protein_ok = protein_delivered >= protein_target
    calories_ok = calorie_delivered >= calorie_target

    # STEP 4: Protein gap → fortifier logic
    protein_gap = protein_target - protein_delivered

    if protein_gap <= 0:
        fortifier = "NO fortifier needed"
    elif protein_gap <= 0.5:
        fortifier = "Use BASIC fortifier"
    elif protein_gap <= 1.0:
        fortifier = "Use INTERMEDIATE fortifier"
    else:
        fortifier = "Use HIGH fortifier"

    return {
        "Milk Calories (kcal/dL)": round(calories, 2),
        "Protein Delivered (g/kg/day)": round(protein_delivered, 2),
        "Calories Delivered (kcal/kg/day)": round(calorie_delivered, 2),
        "Meets Protein Target?": "YES" if protein_ok else "NO",
        "Meets Calorie Target?": "YES" if calories_ok else "NO",
        "Protein Gap": round(protein_gap, 2),
        "Fortifier Recommendation": fortifier
    }


# ------------------------------------------------
# LOAD TRAINED AI MODELS (PHASE 5)
# ------------------------------------------------
model_fat = joblib.load("models/model_fat.pkl")
model_protein = joblib.load("models/model_protein.pkl")
model_lactose = joblib.load("models/model_lactose.pkl")


# ------------------------------------------------
# STREAMLIT UI DESIGN
# ------------------------------------------------
st.title("NICU Milk Nutrition Decision Support System")

# ---- Medical Standards Section ----
with st.expander("📘 Medical Standards (Click to Expand)"):
    st.markdown("""
    **Energy Formula:**  
    Human-milk calories = *(Protein × 4.4) + (Fat × 8.79) + (Lactose × 3.87)* kcal/dL.  
    *Source:* Nature study on human milk energy conversions.[1](https://nin.res.in/dietaryguidelines/pdfjs/locale/DGI_2024.pdf)  

    **Calorie Requirements:**  
    - 110 kcal/kg/day (normal growth)  
    - 135 kcal/kg/day (catch-up growth)  
    *(Neonatal clinical standards)*  
    [1](https://nin.res.in/dietaryguidelines/pdfjs/locale/DGI_2024.pdf)  

    **Protein Requirements:**  
    Preterm infants need **3.5–5.0 g/kg/day** protein.  

    **Feeding Volume Limit:**  
    NICUs use **160 ml/kg/day** as the safe upper limit.[1](https://nin.res.in/dietaryguidelines/pdfjs/locale/DGI_2024.pdf)  

    **Fortifier Need:**  
    Basic fortifier fails in **>75%** of mature donor milk samples.  
    Stronger fortifiers are often required.[1](https://nin.res.in/dietaryguidelines/pdfjs/locale/DGI_2024.pdf)  
    """)


# ---- User Guidance ----
with st.expander("ℹ️ How to Use This App"):
    st.markdown("""
    1. Enter milk values (fat/protein/lactose) manually OR use AI prediction.  
    2. Enter baby’s weight and feeding limits.  
    3. Select protein & calorie targets.  
    4. Click **Calculate Nutrition**.  
    5. View fortifier recommendation & safety alerts.
    """)


# -------------------------------
# MILK INPUT SECTION
# -------------------------------
st.subheader("1. Milk Nutrition Input")

mode = st.radio("Choose Input Method:", ("Enter Manually", "Predict Using AI Model"))

if mode == "Enter Manually":
    fat = st.number_input("Fat (g/dL)", 0.0)
    protein = st.number_input("Protein (g/dL)", 0.0)
    lactose = st.number_input("Lactose (g/dL)", 0.0)

else:
    st.info("AI Prediction Mode Active")

    age_weeks = st.number_input("Age of Milk (Weeks)", 0.0)
    term_category = st.selectbox("Term Category", [0, 1, 2])
    days_between = st.number_input("Days Between Pumps", 0)
    pump_dates = st.number_input("Number of Pump Dates", 1)
    lact_stage = st.selectbox("Lactation Stage", [0, 1, 2])

    x_input = np.array([[term_category, age_weeks, days_between, pump_dates, lact_stage]])

    fat = model_fat.predict(x_input)[0]
    protein = model_protein.predict(x_input)[0]
    lactose = model_lactose.predict(x_input)[0]

    st.success(f"Predicted Fat: {fat:.2f}")
    st.success(f"Predicted Protein: {protein:.2f}")
    st.success(f"Predicted Lactose: {lactose:.2f}")


# -------------------------------
# BABY INFORMATION
# -------------------------------
st.subheader("2. Baby Information")

infant_weight = st.number_input("Infant Weight (kg)", 0.5)
volume_limit = st.number_input("Feeding Volume Limit (ml/kg/day)", 160)

protein_target = st.selectbox("Protein Target (g/kg/day)", [3.5, 4.0, 4.5, 5.0])
calorie_target = st.selectbox("Calorie Target (kcal/kg/day)", [110, 135])


# -------------------------------
# CALCULATE BUTTON
# -------------------------------
if st.button("Calculate Nutrition"):
    result = calculate_milk_nutrition(
        fat, protein, lactose,
        infant_weight, volume_limit,
        protein_target, calorie_target
    )

    st.subheader("Results:")
    for key, value in result.items():
        st.write(f"**{key}:** {value}")