import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Load the Excel file
uploaded_file = st.file_uploader("Upload Uwazi Report Excel File", type=["xlsx"])

if uploaded_file:
    # Load the Assessment Overview sheet
    df = pd.read_excel(uploaded_file, sheet_name="Assessment Overview")

    # Clean the data
    df = df[['Intelligence Area', 'Number of Tasks', 'Tasks_Completed', 'Total Score', 'Student Score', 'Overall %']].dropna()
    df['Overall %'] = pd.to_numeric(df['Overall %'], errors='coerce')

    st.title("📊 Uwazi Talent Report Dashboard")
    st.subheader("🔍 Overview of Multiple Intelligences Performance")

    # Summary metrics
    avg_score = df['Student Score'].mean()
    avg_completion = df['Tasks_Completed'].sum() / df['Number of Tasks'].sum() * 100

    col1, col2 = st.columns(2)
    col1.metric("🧠 Average Score", f"{avg_score:.1f}")
    col2.metric("✅ Task Completion Rate", f"{avg_completion:.1f}%")

    # Bar chart for each intelligence
    st.markdown("### 📚 Scores by Intelligence Area")
    bar_fig = px.bar(
        df,
        x="Intelligence Area",
        y="Student Score",
        color="Intelligence Area",
        text="Student Score",
        title="Scores by Intelligence Type",
    )
    st.plotly_chart(bar_fig, use_container_width=True)

    # Radar chart
    st.markdown("### 🕸️ Radar View of Strengths")
    radar_fig = go.Figure()
    radar_fig.add_trace(go.Scatterpolar(
        r=df['Overall %'],
        theta=df['Intelligence Area'],
        fill='toself',
        name='Overall %'
    ))
    radar_fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
        showlegend=False
    )
    st.plotly_chart(radar_fig, use_container_width=True)

    # Table view
    st.markdown("### 📋 Detailed Performance Table")
    st.dataframe(df.set_index('Intelligence Area'), use_container_width=True)

else:
	    st.info("👆 Please upload the Uwazi Excel report to begin.")

