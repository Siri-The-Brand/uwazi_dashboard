import streamlit as st
import pandas as pd
import json
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO
from fpdf import FPDF
from PIL import Image
import plotly.io as pio
import os

# --- Load access code mapping ---
with open("codes.json") as f:
    code_map = json.load(f)

st.set_page_config(page_title="Uwazi Report", layout="wide")

# --- Custom styling ---
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins&display=swap');
        html, body, [class*="css"] {
            font-family: 'Poppins', sans-serif;
        }
        .stTabs [role="tablist"] {
            border-bottom: 2px solid #25a7a7;
        }
        .stTabs [role="tab"] {
            font-weight: 600;
            font-size: 16px;
            padding: 12px;
            margin-right: 16px;
        }
        .stAlert-success {
            font-size: 15px;
        }
    </style>
""", unsafe_allow_html=True)

# --- Page title ---
st.title("📘 Uwazi Report Dashboard")
st.subheader("Login to view your personalized talent insights")

# --- Access code login ---
access_code = st.text_input("Enter your access code (e.g., A654L, B87J)").strip().upper()

# --- If valid code ---
if access_code in code_map:
    file_path = f"uwazi_reports/{code_map[access_code]}"

    try:
        overview_df = pd.read_excel(file_path, sheet_name="Assessment Overview")
        task_df = pd.read_excel(file_path, sheet_name="Task Scores")
        summary_df = pd.read_excel(file_path, sheet_name="Summary", header=None)
        solver_info_df = pd.read_excel(file_path, sheet_name="Siri Solvers Info")
        career_df = pd.read_excel(file_path, sheet_name="Career Suggestions")

        student_name = solver_info_df.iloc[0, 1]
        top_intelligence = solver_info_df.iloc[0, 3]
        shaba_track = solver_info_df.iloc[0, 4]
        report_summary = summary_df.iloc[1, 2]

        st.success(f"🎉 Welcome, {student_name}! This report summarizes your performance across 99 psychometric tasks.")
        st.markdown("📌 *Use the clearly labeled tabs below to explore intelligence insights, detailed task breakdowns, and personalized recommendations.*")
        st.markdown("⚠️ *Disclaimer: This report is for developmental purposes only. It is not a clinical or diagnostic tool.*")

        # --- TABS ---
        tab1, tab2, tab3, tab4 = st.tabs(["🧠 Overview", "🧩 Task Insights", "🎯 Career Recommendations", "📥 Download Report"])

        # --- TAB 1: Overview ---
        with tab1:
            st.markdown("### 📝 Summary Overview")
            st.markdown(report_summary)

            col1, col2 = st.columns(2)
            avg_score = overview_df['Student Score'].mean()
            completion = (overview_df['Tasks_Completed'].sum() / overview_df['Number of Tasks'].sum()) * 100
            col1.metric("📈 Average Score", f"{avg_score:.1f}")
            col2.metric("✅ Task Completion", f"{completion:.1f}%")

            st.markdown("### 📊 Scores by Intelligence")
            bar_fig = px.bar(overview_df, x="Intelligence Area", y="Student Score", text="Student Score", color="Intelligence Area")
            st.plotly_chart(bar_fig, use_container_width=True)

            st.markdown("### 🕸️ Overall Intelligence Strengths")
            radar_fig = go.Figure()
            radar_fig.add_trace(go.Scatterpolar(r=overview_df["Overall %"], theta=overview_df["Intelligence Area"], fill="toself"))
            radar_fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), showlegend=False)
            st.plotly_chart(radar_fig, use_container_width=True)

        # --- TAB 2: Task Insights ---
        with tab2:
            st.markdown("### 🧩 Task Scores and Insights")
            st.markdown("""
            Each intelligence was tested using multiple tasks. These scores (out of 5) reveal specific elements of strength or development areas.
            You can use this to explore patterns within each intelligence type.
            """)
            st.dataframe(task_df[["Intelligence Area", "Task", "Score (out of 5)", "Comments"]])

        # --- TAB 3: Career Recommendations ---
        with tab3:
            st.markdown("### 🎯 Career & Shaba Recommendations")
            st.markdown(f"**🌟 Top Intelligence**: `{top_intelligence}`")
            st.markdown(f"**🎓 Recommended Shaba Track**: `{shaba_track}`")

            st.markdown("#### 🔍 Career Matches")
            st.write(", ".join(career_df["Career"].dropna().head(5)))

            st.markdown("#### 🎓 Recommended University Degrees")
            st.write(", ".join(career_df["Related University Degrees (Kenya/Online)"].dropna().head(5)))

            st.markdown("#### 🛠 Recommended TVET Courses")
            st.write(", ".join(career_df["Related TVET Courses (Kenya/Online)"].dropna().head(5)))

            st.markdown("#### 🏫 Suggested Schools")
            st.write(", ".join(career_df["School"].dropna().head(5)))

        # --- TAB 4: PDF Export ---
        with tab4:
            st.markdown("### 📥 Export Your Report")

            def safe_text(text):
                return text.encode("latin1", "replace").decode("latin1")

            def generate_pdf():
                bar_img = BytesIO()
                radar_img = BytesIO()
                pio.write_image(bar_fig, bar_img, format="png")
                pio.write_image(radar_fig, radar_img, format="png")
                bar_img.seek(0)
                radar_img.seek(0)

                Image.open(bar_img).save("bar_chart.png")
                Image.open(radar_img).save("radar_chart.png")

                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Arial", size=12)

                pdf.set_font("Arial", "B", 14)
                pdf.cell(0, 10, safe_text(f"Uwazi Talent Report – {student_name}"), ln=True, align="C")
                pdf.ln(6)

                pdf.set_font("Arial", "B", 12)
                pdf.cell(0, 10, "Intelligence Summary", ln=True)
                pdf.set_font("Arial", size=11)
                for _, row in overview_df.iterrows():
                    line = f"{row['Intelligence Area']}: {row['Student Score']} ({row['Overall %']}%)"
                    pdf.cell(0, 8, safe_text(line), ln=True)

                pdf.ln(5)
                pdf.cell(0, 10, "Visual Insights", ln=True)
                pdf.image("bar_chart.png", x=10, w=180)
                pdf.ln(5)
                pdf.image("radar_chart.png", x=10, w=180)

                pdf.ln(8)
                pdf.set_font("Arial", "B", 12)
                pdf.cell(0, 10, "Career Recommendations", ln=True)
                pdf.set_font("Arial", size=11)
                pdf.multi_cell(0, 8, safe_text(f"Top Intelligence: {top_intelligence}"))
                pdf.multi_cell(0, 8, safe_text(f"Recommended Shaba Track: {shaba_track}"))

                pdf.multi_cell(0, 8, safe_text("Suggested Careers: " + ", ".join(career_df["Career"].dropna().head(5))))
                pdf.multi_cell(0, 8, safe_text("University Programs: " + ", ".join(career_df["Related University Degrees (Kenya/Online)"].dropna().head(5))))
                pdf.multi_cell(0, 8, safe_text("TVET Programs: " + ", ".join(career_df["Related TVET Courses (Kenya/Online)"].dropna().head(5))))
                pdf.multi_cell(0, 8, safe_text("Schools: " + ", ".join(career_df["School"].dropna().head(5))))

                pdf.ln(5)
                pdf.set_font("Arial", "I", size=9)
                pdf.multi_cell(0, 6, safe_text("Disclaimer: This report is for developmental purposes only. It is not a clinical or diagnostic tool."))

                pdf_text = pdf.output(dest="S")
                pdf_bytes = pdf_text.encode("latin1", "replace")
                return BytesIO(pdf_bytes)

            st.download_button(
                label="📥 Download PDF Report",
                data=generate_pdf(),
                file_name=f"{student_name}_Uwazi_Report.pdf",
                mime="application/pdf"
            )

    except Exception as e:
        st.error("❌ Failed to load your report. Please contact support.")
        st.exception(e)

elif access_code:
    st.error("❌ Access code not recognized. Please try again.")
else:
    st.info("ℹ️ Please enter your access code to view your report.")
