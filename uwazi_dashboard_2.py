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

# Custom style for better tab visibility
st.markdown("""
    <style>
        .stTabs [role="tablist"] {
            border-bottom: 2px solid #ff4b4b;
        }
        .stTabs [role="tab"] {
            font-weight: bold;
            font-size: 16px;
            padding: 12px;
            margin-right: 12px;
        }
        .stAlert-success {
            font-size: 15px;
        }
    </style>
""", unsafe_allow_html=True)

st.title("📘 Uwazi Report Dashboard")
st.subheader("Login to view your personalized talent insights")

# --- Access Code Input ---
access_code = st.text_input("Enter your access code (e.g., A654L, B87J)").strip().upper()

if access_code in code_map:
    file_path = f"uwazi_reports/{code_map[access_code]}"

    try:
        # Load all needed sheets
        overview_df = pd.read_excel(file_path, sheet_name="Assessment Overview")
        task_df = pd.read_excel(file_path, sheet_name="Task Scores")
        summary_df = pd.read_excel(file_path, sheet_name="Summary", header=None)
        solver_info_df = pd.read_excel(file_path, sheet_name="Siri Solvers Info")
        career_df = pd.read_excel(file_path, sheet_name="Career Suggestions")

        # Extract key details
        student_name = solver_info_df.iloc[0, 1] if not solver_info_df.empty else "Unnamed Solver"
        top_intelligence = solver_info_df.iloc[0, 3] if len(solver_info_df.columns) > 3 else "Not Available"
        shaba_track = solver_info_df.iloc[0, 4] if len(solver_info_df.columns) > 4 else "Not Available"
        report_summary = summary_df.iloc[1, 2] if not summary_df.empty else "No summary available"

        st.success(f"🎉 Welcome, {student_name}!\n\nThis report summarizes your performance across 99 psychometric tasks in the Uwazi assessment. It is intended to give insight into your learning strengths and future pathways.")

        st.markdown("📌 *Use the tabs below to explore intelligence insights, task scores, and personalized recommendations.*")
        st.markdown("⚠️ *Disclaimer: This report is for educational and personal development purposes only. It does not replace professional clinical or psychological evaluations.*")

        # --- Tabs Layout ---
        tab1, tab2, tab3, tab4 = st.tabs([
            "🧠 Overview", "🧩 Task Insights", "🎯 Career Recommendations", "📥 Download Report"
        ])

        with tab1:
            st.markdown("### 📝 Summary Overview")
            st.markdown(report_summary)

            col1, col2 = st.columns(2)
            avg_score = overview_df['Student Score'].mean()
            task_completion = (overview_df['Tasks_Completed'].sum() / overview_df['Number of Tasks'].sum()) * 100
            col1.metric("📈 Average Score", f"{avg_score:.1f}")
            col2.metric("✅ Task Completion", f"{task_completion:.1f}%")

            st.markdown("### 📊 Scores by Intelligence")
            bar_fig = px.bar(
                overview_df, x="Intelligence Area", y="Student Score",
                text="Student Score", color="Intelligence Area"
            )
            st.plotly_chart(bar_fig, use_container_width=True)

            st.markdown("### 🕸️ Overall Intelligence Strengths")
            radar_fig = go.Figure()
            radar_fig.add_trace(go.Scatterpolar(
                r=overview_df["Overall %"],
                theta=overview_df["Intelligence Area"],
                fill="toself"
            ))
            radar_fig.update_layout(
                polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
                showlegend=False
            )
            st.plotly_chart(radar_fig, use_container_width=True)

        with tab2:
            st.markdown("### 🧩 Task Scores and Insights")
            st.markdown("""
            Each intelligence area is assessed through targeted tasks aligned to its core elements. 
            The scores below reflect how the learner performed on each task (out of 5). 
            This helps us identify not only the strongest intelligences, but also specific elements the learner excels in or struggles with.
            """)
            st.dataframe(task_df[["Intelligence Area", "Task", "Score (out of 5)", "Comments"]])

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

        with tab4:
            st.markdown("### 📥 Export Your Report")

            def generate_pdf():
                # Save bar and radar plots to memory
                bar_img = BytesIO()
                radar_img = BytesIO()
                pio.write_image(bar_fig, bar_img, format="png")
                pio.write_image(radar_fig, radar_img, format="png")
                bar_img.seek(0)
                radar_img.seek(0)

                bar_path = "bar_chart.png"
                radar_path = "radar_chart.png"
                Image.open(bar_img).save(bar_path)
                Image.open(radar_img).save(radar_path)

                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Arial", size=12)
                pdf.set_fill_color(240, 240, 240)

                pdf.set_font("Arial", "B", 14)
                pdf.cell(0, 10, f"Uwazi Talent Report – {student_name}", ln=True, align="C")
                pdf.ln(6)

                pdf.set_font("Arial", "B", 12)
                pdf.cell(0, 10, "Intelligence Summary", ln=True)
                pdf.set_font("Arial", size=11)
                for _, row in overview_df.iterrows():
                    pdf.cell(0, 8, f"{row['Intelligence Area']}: {row['Student Score']} ({row['Overall %']}%)", ln=True)

                pdf.ln(5)
                pdf.set_font("Arial", "B", 12)
                pdf.cell(0, 10, "Visual Insights", ln=True)
                pdf.image(bar_path, x=10, w=180)
                pdf.ln(5)
                pdf.image(radar_path, x=10, w=180)

                pdf.ln(8)
                pdf.set_font("Arial", "B", 12)
                pdf.cell(0, 10, "Career Recommendations", ln=True)
                pdf.set_font("Arial", size=11)
                pdf.multi_cell(0, 8, f"Top Intelligence: {top_intelligence}")
                pdf.multi_cell(0, 8, f"Recommended Shaba Track: {shaba_track}")

                careers = ", ".join(career_df["Career"].dropna().head(5))
                degrees = ", ".join(career_df["Related University Degrees (Kenya/Online)"].dropna().head(5))
                tvets = ", ".join(career_df["Related TVET Courses (Kenya/Online)"].dropna().head(5))
                schools = ", ".join(career_df["School"].dropna().head(5))

                pdf.multi_cell(0, 8, f"Suggested Careers: {careers}")
                pdf.multi_cell(0, 8, f"University Programs: {degrees}")
                pdf.multi_cell(0, 8, f"TVET Programs: {tvets}")
                pdf.multi_cell(0, 8, f"Schools: {schools}")

                pdf.set_font("Arial", "I", size=9)
                pdf.ln(4)
                pdf.multi_cell(0, 6, "Disclaimer: This report is for developmental purposes only. Not a diagnostic tool or substitute for licensed psychological evaluation.")

                pdf_bytes = pdf.output(dest="S").encode("latin1")
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
