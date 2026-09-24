import streamlit as st
import pandas as pd
from engine import RuleBasedStockEngine

st.set_page_config(page_title="Symax Stock Assistant", layout="wide")
st.title("🧪 Symax Laboratories - DEMO")

@st.cache_resource
def load_engine():
    return RuleBasedStockEngine("Symax_AI_Stock_Assessment_100plus.xlsx")

engine = load_engine()

st.sidebar.header("System Diagnostics")
st.sidebar.metric("Valid Stock Records", len(engine.valid_stock))
st.sidebar.metric("Anomalies Flagged", len(engine.anomalies))

if st.sidebar.checkbox("View Quarantined Data Anomalies"):
    st.sidebar.subheader("Zero/Negative Quantities & Unknown Locations")
    st.sidebar.dataframe(engine.anomalies[['Stock_ID', 'CAS_Number', 'Quantity', 'Location']])

st.subheader("💬 Ask the Assistant in Natural Language")
sample_query = st.selectbox(
    "Select an example question or choose custom query:",
    [
        "Custom Query...",
        "what is the stock of n-Butyllithium 1.6 M Hexane?",
        "What is the stock of CAS 109-72-8?",
        "How much is available in Hyderabad?",
        "Which concentrations are available for CAS 109-72-8?",
        "Which products are below minimum stock?",
        "Which products are available in Hyderabad but not Bangalore?"
    ]
)

if sample_query != "Custom Query...":
    user_input = st.text_input("Enter your question:", value=sample_query)
else:
    user_input = st.text_input("Enter your question:", value="what is the stock of n-Butyllithium 1.6 M Hexane?")

if st.button("Ask Assistant"):
    if user_input:
        results, explainability_trace = engine.parse_and_query(user_input)
        
        st.info(f"🔍 **Explainability Log**: {explainability_trace}")
        
        if isinstance(results, str):
            st.warning(results)
        elif isinstance(results, pd.DataFrame):
            if results.empty:
                st.warning("No matching inventory records found.")
            else:
                st.dataframe(results)
                
                if "CHECK_LOW_STOCK" in explainability_trace and not results.empty:
                    st.subheader("🤖 Automated Purchase Requirement Generator")
                    for idx, row in results.iterrows():
                        st.error(f"**PURCHASE ALERT**: `{row['Product_Clean']}` (CAS: `{row['CAS_Clean']}`, Conc: `{row['Conc_Clean']}`) is short by **{row['Deficit']} {row['Unit']}** (Threshold: {row['Threshold']}, Current Total Stock: {row['Quantity']}).")