import streamlit as st
import pandas as pd
import json
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
from io import BytesIO
from PIL import Image
from fpdf import FPDF

# --- Load access code mapping ---
with open("codes.json") as f:
    code_map = json.load(f)

st.set_page_config(page_title="Uwazi Report", layout="wide")

# --- UI Styling for Tabs & Alerts ---
st.markdown("""
    <style>
        .stTabs [role="tablist"] { border-bottom: 2px solid #009999; }
        .stTabs [role="tab"] { font-weight: bold; font-size: 16px; padding: 12px; margin-right: 12px; }
        .stAlert-success { font-size: 15px; }
    </style>
""", unsafe_allow_html=True)

st.title("📘 Uwazi Report Dashboard")
st.subheader("Login to view your personalized talent insights")

access_code = st.text_input("Enter your access code (e.g., A654L, B87J)").strip().upper()

if access_code in code_map:
    file_path = f"uwazi_reports/{code_map[access_code]}"
    try:
        # — Load sheets —
        overview_df    = pd.read_excel(file_path, sheet_name="Assessment Overview")
        task_df        = pd.read_excel(file_path, sheet_name="Task Scores")
        summary_df     = pd.read_excel(file_path, sheet_name="Summary", header=None)
        solver_info_df = pd.read_excel(file_path, sheet_name="Siri Solvers Info")
        career_df      = pd.read_excel(file_path, sheet_name="Career Suggestions")

        # — Extract key fields —
        student_name   = solver_info_df.iloc[0,1] if not solver_info_df.empty else "Unnamed Solver"
        top_intel      = solver_info_df.iloc[0,3] if solver_info_df.shape[1]>3 else "N/A"
        shaba_track    = solver_info_df.iloc[0,4] if solver_info_df.shape[1]>4 else "N/A"
        report_summary = summary_df.iloc[1,2]  if summary_df.shape[0]>1 else "No summary available"

        # — Welcome & instructions —
        st.success(
            f"🎉 Welcome, {student_name}!  \n"
            "This report summarizes your performance across **99 psychometric tasks** in the Uwazi assessment."
        )
        st.markdown("📌 *Click the tabs below to explore your results.*  ")
        st.markdown(
            "⚠️ *Disclaimer: This report is for personal development only. Not a clinical or psychological diagnosis.*"
        )
        st.markdown("🎖️ *Soma Siri Afrika is an award winning innovation as well as a member of the Career Developers Association of Kenya.* The Uwazi™️ and Siri MaP™️ are global patents. From Afrika, with love.")

        # — Tabs —
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "🧠 Overview",
            "🧩 Task Insights",
            "🎯 Career Recommendations",
            "🔍 About Uwazi",
            "📥 Download Report"
        ])

        # — Tab 1: Overview —
        with tab1:
            st.markdown("### 📝 Summary Overview")
            st.info(report_summary)

            c1, c2 = st.columns(2)
            avg_score      = overview_df["Student Score"].mean()
            completion_pct = overview_df["Tasks_Completed"].sum() / overview_df["Number of Tasks"].sum() * 100
            c1.metric("📈 Uwazi Composite Insight Score", f"{avg_score:.1f}")
            c2.metric("✅ Task Completion", f"{completion_pct:.1f}%")

            st.markdown("### 📊 Scores by Intelligence")
            bar_fig = px.bar(
                overview_df,
                x="Intelligence Area", y="Student Score",
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
                polar=dict(radialaxis=dict(visible=True, range=[0,100])),
                showlegend=False
            )
            st.plotly_chart(radar_fig, use_container_width=True)

        # — Tab 2: Task Insights —
        with tab2:
            st.markdown("### 🧩 Task Scores and Insights")
            st.markdown("""
                Each task targets an element within an intelligence area.
                Scores (out of 5) highlight where you excel or may wish to grow.
            """)
            st.dataframe(
                task_df[["Intelligence Area","Task","Score (out of 5)","Comments"]],
                use_container_width=True
            )

        # — Tab 3: Career & Shaba —
        with tab3:
            st.markdown("### 🎯 Career & Shaba Recommendations")
            st.markdown(f"**🌟 Top Intelligence**: `{top_intel}`")
            st.markdown(f"**🎓 Recommended Shaba Track**: `{shaba_track}`")

            st.markdown("#### 🔍 Career Matches")
            st.write(", ".join(career_df["Career"].dropna().head(5)))

            st.markdown("#### 🎓 Recommended University Degrees")
            st.write(", ".join(career_df["Related University Degrees (Kenya/Online)"].dropna().head(5)))

            st.markdown("#### 🛠 Recommended TVET Courses")
            st.write(", ".join(career_df["Related TVET Courses (Kenya/Online)"].dropna().head(5)))

            st.markdown("#### 🏫 Suggested Schools")
            st.write(", ".join(career_df["School"].dropna().head(5)))

        # — Tab 4: About Uwazi —
        with tab4:
            st.header("🔍 Why Soma Siri Afrika, Uwazi & Shaba")

            st.subheader("In a world where AI can do nearly all tasks … What truly matters?")
            st.markdown("""
            ❓ **What uniquely human skills** should our children be cultivating today?
            Uwazi dives deep—beyond rote learning—to uncover innate strengths and 21st-century mindsets. Do they need to learn computers and coding to catch up, or is there a different path that is uniquely theirs?
            """)

            st.subheader("🌍 Soma Siri Afrika")
            st.markdown("""
                        -The world's first innovation incubator for kids and youth using AI, Psychology and education to prep super heroes for Afrika
            - Pan-African mission to discover and nurture each child’s innate talents  
            - Blends educational neuroscience with our rich cultural heritage  
            - Uses real, hands-on psychometric tasks—not just surveys  
            """)

            st.subheader("🧠 Uwazi for Excans")
            st.markdown("""
            **99-Task Talent Triage**  
            - Eight core intelligences (Linguistic, Logical-Mathematical, Spatial, etc.)  
            - Plus entrepreneurial thinking & creative problem solving  

            **Key Benefits**  
            1. **Strength-Based Insights**: Personalized development blueprints  
            2. **Early Advantage**: Identify talents from age 6  
            3. **Growth Tracking**: Quarterly mini-reassessments on your dashboard  
            """)

            st.subheader("🚀 Shaba Level")
            st.markdown("""
            **Strength-First Pathways**  
            - Customised courses based on this Uwazi Report*  
            - Small-group coaching by certified specialists  
            - Blended live labs + self-paced modules
            - Can be accessed fully online
            - Real-world challenges (hackathons, design sprints)  
            """)

            st.subheader("🏆 Family Perks & Next Steps")
            perks = st.columns(3)
            perks[0].markdown("**1. Congrats on completing level 1: Uwazi.")
            perks[1].markdown("**2. Upgrade to Shaba Level**  \nStart on your 12week nanodegree and get work as soon as you are done!.")
            perks[2].markdown("**3. Parent Portal**  \nDashboards, alerts & coaching tips. - COMING SOON")

            st.markdown("""
            🏅 *Families report a **90% boost** in engagement when learning aligns  
            with natural strengths. Kids report learning for longer hours than ever before - this is talent led education. \nYou may Enroll for Uwazi 4-7 years, 8-12 years or 13-17 years**  \nEarly-bird mini-snapshot included.*
            """)

        # — Tab 5: Download Report —
        with tab5:
            st.markdown("### 📥 Export Your Full Report with Charts & Insights")

            def generate_pdf():
                # render charts
                bar_buf, radar_buf = BytesIO(), BytesIO()
                pio.write_image(bar_fig,   bar_buf,   format="png")
                pio.write_image(radar_fig, radar_buf, format="png")
                bar_buf.seek(0); radar_buf.seek(0)
                Image.open(bar_buf).save("bar_chart.png")
                Image.open(radar_buf).save("radar_chart.png")

                # build PDF
                pdf = FPDF()
                pdf.add_font("Poppins", "", "fonts/Poppins-Regular.ttf", uni=True)
                pdf.add_font("Poppins", "B", "fonts/Poppins-Bold.ttf", uni=True)
                pdf.add_font("Poppins", "I", "fonts/Poppins-Italic.ttf", uni=True)
                pdf.set_auto_page_break(True, 15)
                pdf.add_page()
                epw = pdf.w - pdf.l_margin - pdf.r_margin

                pdf.set_font("Poppins", "B", 14)
                pdf.cell(0, 10, f"Uwazi Talent Report – {student_name}", ln=True, align="C")
                pdf.ln(6)

                # Summary
                pdf.set_font("Poppins", "", 11)
                pdf.multi_cell(epw, 8, report_summary)

                # Intelligence scores
                pdf.ln(5)
                pdf.set_font("Poppins", "B", 12)
                pdf.cell(0, 10, "Scores by Intelligence", ln=True)
                pdf.set_font("Poppins", "", 11)
                for _, r in overview_df.iterrows():
                    line = f"{r['Intelligence Area']}: {r['Student Score']} ({r['Overall %']}%)"
                    pdf.multi_cell(epw, 8, line)

                # Charts
                pdf.ln(5)
                pdf.set_font("Poppins", "B", 12)
                pdf.cell(0, 10, "Visual Insights", ln=True)
                pdf.image("bar_chart.png", x=pdf.l_margin, w=epw)
                pdf.ln(4)
                pdf.image("radar_chart.png", x=pdf.l_margin, w=epw)

                # Career recs
                pdf.ln(6)
                pdf.set_font("Poppins", "B", 12)
                pdf.cell(0, 10, "Career Recommendations", ln=True)
                pdf.set_font("Poppins", "", 11)
                pdf.multi_cell(epw, 8, f"Top Intelligence: {top_intel}")
                pdf.multi_cell(epw, 8, f"Recommended Shaba Track: {shaba_track}")

                careers = ", ".join(career_df["Career"].dropna().head(5))
                degrees = ", ".join(career_df["Related University Degrees (Kenya/Online)"].dropna().head(5))
                tvets   = ", ".join(career_df["Related TVET Courses (Kenya/Online)"].dropna().head(5))
                schools = ", ".join(career_df["School"].dropna().head(5))
                pdf.multi_cell(epw, 8, f"Suggested Careers: {careers}")
                pdf.multi_cell(epw, 8, f"University Programs: {degrees}")
                pdf.multi_cell(epw, 8, f"TVET Courses: {tvets}")
                pdf.multi_cell(epw, 8, f"Schools: {schools}")

                # Footer disclaimer
                pdf.ln(4)
                pdf.set_font("Poppins", "I", 9)
                pdf.multi_cell(
                    epw, 6,
                    "⚠️ This report is for personal development only. "
                    "Not a substitute for licensed psychological evaluation."
                )

                return BytesIO(pdf.output(dest="S"))

            st.download_button(
                "📥 Download PDF Report",
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
