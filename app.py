import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ----------------------------------
# PAGE CONFIG
# ----------------------------------
st.set_page_config(
    page_title="Startup Analytics Dashboard",
    page_icon="🚀",
    layout="wide"
)

# ----------------------------------
# CUSTOM CSS
# ----------------------------------
st.markdown("""
<style>
.metric-card{
    background:#0f172a;
    padding:20px;
    border-radius:15px;
    text-align:center;
}
</style>
""", unsafe_allow_html=True)

# ----------------------------------
# LOAD DATA
# ----------------------------------

@st.cache_data
def load_data():
    return pd.read_csv("data/startup_data.csv")

df = load_data()

# ----------------------------------
# HEADER
# ----------------------------------

st.title("🚀 Startup Ecosystem Analytics Dashboard")
st.markdown("Deep exploratory analysis of startup performance and growth.")

# ----------------------------------
# SIDEBAR
# ----------------------------------

st.sidebar.header("Filters")

industry = st.sidebar.multiselect(
    "Industry",
    df["Industry"].unique(),
    default=df["Industry"].unique()
)

region = st.sidebar.multiselect(
    "Region",
    df["Region"].unique(),
    default=df["Region"].unique()
)

exit_status = st.sidebar.multiselect(
    "Exit Status",
    df["Exit Status"].unique(),
    default=df["Exit Status"].unique()
)

filtered_df = df[
    (df["Industry"].isin(industry))
    & (df["Region"].isin(region))
    & (df["Exit Status"].isin(exit_status))
]

# ----------------------------------
# KPI SECTION
# ----------------------------------

st.subheader("📈 Executive Overview")

col1,col2,col3,col4 = st.columns(4)

with col1:
    st.metric(
        "Total Startups",
        f"{filtered_df.shape[0]:,}"
    )

with col2:
    st.metric(
        "Total Funding",
        f"${filtered_df['Funding Amount (M USD)'].sum():,.0f} M"
    )

with col3:
    st.metric(
        "Total Revenue",
        f"${filtered_df['Revenue (M USD)'].sum():,.0f} M"
    )

with col4:
    profit_rate = (
        filtered_df["Profitable"].mean()*100
    )
    st.metric(
        "Profitable %",
        f"{profit_rate:.1f}%"
    )

# ----------------------------------
# INDUSTRY ANALYSIS
# ----------------------------------

st.subheader("🏭 Industry Analysis")

col1,col2 = st.columns(2)

industry_funding = (
    filtered_df.groupby("Industry")
    ["Funding Amount (M USD)"]
    .sum()
    .reset_index()
)

fig = px.bar(
    industry_funding,
    x="Industry",
    y="Funding Amount (M USD)",
    title="Funding by Industry"
)

col1.plotly_chart(fig,use_container_width=True)

industry_rev = (
    filtered_df.groupby("Industry")
    ["Revenue (M USD)"]
    .mean()
    .reset_index()
)

fig = px.pie(
    industry_rev,
    names="Industry",
    values="Revenue (M USD)",
    title="Revenue Distribution"
)

col2.plotly_chart(fig,use_container_width=True)

# ----------------------------------
# REGION ANALYSIS
# ----------------------------------

st.subheader("🌎 Regional Analysis")

regional = (
    filtered_df.groupby("Region")
    .agg({
        "Valuation (M USD)":"mean",
        "Revenue (M USD)":"mean"
    })
    .reset_index()
)

fig = px.bar(
    regional,
    x="Region",
    y="Valuation (M USD)",
    color="Revenue (M USD)",
    title="Average Valuation by Region"
)

st.plotly_chart(fig,use_container_width=True)

# ----------------------------------
# FUNDING VS VALUATION
# ----------------------------------

st.subheader("💰 Funding vs Valuation")

fig = px.scatter(
    filtered_df,
    x="Funding Amount (M USD)",
    y="Valuation (M USD)",
    size="Employees",
    color="Industry",
    hover_name="Startup Name",
    title="Funding vs Valuation"
)

st.plotly_chart(fig,use_container_width=True)

# ----------------------------------
# PROFITABILITY ANALYSIS
# ----------------------------------

st.subheader("📊 Profitability Analysis")

profit_df = (
    filtered_df.groupby("Industry")
    ["Profitable"]
    .mean()
    .reset_index()
)

profit_df["Profitable"] *= 100

fig = px.bar(
    profit_df,
    x="Industry",
    y="Profitable",
    color="Profitable",
    title="Profitability Rate by Industry"
)

st.plotly_chart(fig,use_container_width=True)

# ----------------------------------
# STARTUP AGE ANALYSIS
# ----------------------------------

st.subheader("⏳ Startup Age Analysis")

current_year = 2025

filtered_df["Startup Age"] = (
    current_year -
    filtered_df["Year Founded"]
)

fig = px.histogram(
    filtered_df,
    x="Startup Age",
    nbins=20,
    title="Startup Age Distribution"
)

st.plotly_chart(fig,use_container_width=True)

# ----------------------------------
# EXIT STATUS ANALYSIS
# ----------------------------------

st.subheader("🏁 Exit Status")

fig = px.sunburst(
    filtered_df,
    path=["Exit Status","Industry"],
    values="Revenue (M USD)"
)

st.plotly_chart(fig,use_container_width=True)

# ----------------------------------
# CORRELATION HEATMAP
# ----------------------------------

st.subheader("🔥 Correlation Analysis")

numeric_cols = [
    "Funding Rounds",
    "Funding Amount (M USD)",
    "Valuation (M USD)",
    "Revenue (M USD)",
    "Employees",
    "Market Share (%)"
]

corr = filtered_df[numeric_cols].corr()

fig = px.imshow(
    corr,
    text_auto=True,
    aspect="auto",
    title="Correlation Matrix"
)

st.plotly_chart(fig,use_container_width=True)

# ----------------------------------
# TOP STARTUPS
# ----------------------------------

st.subheader("🏆 Top Startups")

top_df = filtered_df.nlargest(
    15,
    "Valuation (M USD)"
)[[
    "Startup Name",
    "Industry",
    "Valuation (M USD)",
    "Revenue (M USD)",
    "Employees"
]]

st.dataframe(
    top_df,
    use_container_width=True
)

# ----------------------------------
# AI INSIGHTS
# ----------------------------------

st.subheader("🧠 Automated Insights")

best_industry = (
    filtered_df.groupby("Industry")
    ["Revenue (M USD)"]
    .mean()
    .idxmax()
)

highest_region = (
    filtered_df.groupby("Region")
    ["Valuation (M USD)"]
    .mean()
    .idxmax()
)

st.success(
    f"""
    • Highest average revenue industry: {best_industry}

    • Highest valuation region: {highest_region}

    • Profitability Rate: {profit_rate:.1f}%

    • Total Funding Raised: ${filtered_df['Funding Amount (M USD)'].sum():,.0f} M
    """
)
