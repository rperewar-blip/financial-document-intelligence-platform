import streamlit as st
import pandas as pd
import tempfile
import os

from extractor import process_document
from commentary import generate_comparison_commentary

st.set_page_config(
    page_title="Financial Doc Intelligence",
    page_icon="📄",
    layout="wide"
)

st.title("AI-Powered Financial Document Intelligence Platform")
st.caption("Transform annual reports and SEC filings into actionable financial insights using AI.")

uploaded_files = st.file_uploader(
    "Upload 10-K / Annual Report PDF(s)",
    type=["pdf"],
    accept_multiple_files=True
)

if uploaded_files:
    st.subheader("Company Names")

    company_names = {}

    for f in uploaded_files:
        company_names[f.name] = st.text_input(
            f"Company name for {f.name}",
            value=f.name.replace(".pdf", "").replace("_", " ").upper()
        )

    if st.button("Analyze Documents"):
        all_data = []

        for f in uploaded_files:
            company_name = company_names[f.name]

            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                tmp.write(f.read())
                tmp_path = tmp.name

            with st.spinner(f"Extracting metrics from {company_name}..."):
                data = process_document(tmp_path, company_name)
                all_data.append(data)

            os.unlink(tmp_path)

        df = pd.DataFrame(all_data)

        st.success("Analysis complete.")

        st.subheader("Executive Summary")

        col1, col2, col3, col4 = st.columns(4)

        top_revenue = df.loc[df["revenue"].idxmax()]
        top_income = df.loc[df["net_income"].idxmax()]

        col1.metric("Companies Analyzed", len(df))
        col2.metric("Top Revenue Company", top_revenue["company"])
        col3.metric("Highest Revenue", f"${top_revenue['revenue']:,.0f}M")
        col4.metric("Highest Net Income", f"{top_income['company']}")

        st.subheader("Extracted Financial Metrics")
        st.caption("Values are shown in millions USD.")

        st.dataframe(
            df.set_index("company"),
            use_container_width=True
        )

        st.subheader("Company Comparison Charts")

        chart_df = df.set_index("company")[[
            "revenue",
            "gross_profit",
            "operating_income",
            "net_income",
            "total_assets",
            "total_debt",
            "cash_flow_ops"
        ]]

        st.bar_chart(chart_df[["revenue", "net_income", "cash_flow_ops"]])
        st.bar_chart(chart_df[["total_assets", "total_debt"]])

        with st.spinner("Generating AI analyst commentary..."):
            commentary = generate_comparison_commentary(all_data)

        st.subheader("AI-Generated Analyst Commentary")
        st.write(commentary)

        csv = df.to_csv(index=False)

        st.download_button(
            "Download Comparison Table CSV",
            csv,
            "financial_comparison.csv",
            "text/csv"
        )