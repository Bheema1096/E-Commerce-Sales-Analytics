from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="E-Commerce Sales Analytics",
    page_icon="📊",
    layout="wide"
)


# --------------------------------------------------
# LOAD DATASET
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_FILE = PROJECT_ROOT / "global_ecommerce_sales.csv"

df = pd.read_csv(DATA_FILE)

df["Order_Date"] = pd.to_datetime(
    df["Order_Date"],
    errors="coerce"
)

df["Year"] = df["Order_Date"].dt.year
df["Month_Number"] = df["Order_Date"].dt.month
df["Month"] = df["Order_Date"].dt.strftime("%b")


# --------------------------------------------------
# TITLE
# --------------------------------------------------

st.title("📊 E-Commerce Sales and Product Analytics Dashboard")

st.write(
    "Analyze global e-commerce sales, profit, products, "
    "categories, countries, regions, and time-based trends."
)


# --------------------------------------------------
# SIDEBAR FILTERS
# --------------------------------------------------

st.sidebar.header("🔎 Dashboard Filters")


# Country
countries = sorted(
    df["Country"].dropna().unique().tolist()
)

selected_country = st.sidebar.selectbox(
    "Country",
    ["All Countries"] + countries
)


# Filter data after country selection
country_df = df.copy()

if selected_country != "All Countries":
    country_df = country_df[
        country_df["Country"] == selected_country
    ]


# Region
regions = sorted(
    country_df["Region"].dropna().unique().tolist()
)

selected_region = st.sidebar.selectbox(
    "Region",
    ["All Regions"] + regions
)


# Product Category
categories = sorted(
    country_df["Product_Category"].dropna().unique().tolist()
)

selected_category = st.sidebar.selectbox(
    "Product Category",
    ["All Categories"] + categories
)


# Year
years = sorted(
    country_df["Year"].dropna().unique().tolist(),
    reverse=True
)

selected_year = st.sidebar.selectbox(
    "Year",
    ["All Years"] + years
)


# Customer Segment
segments = sorted(
    country_df["Customer_Segment"].dropna().unique().tolist()
)

selected_segment = st.sidebar.selectbox(
    "Customer Segment",
    ["All Segments"] + segments
)


# --------------------------------------------------
# APPLY ALL FILTERS
# --------------------------------------------------

filtered_df = country_df.copy()

if selected_region != "All Regions":
    filtered_df = filtered_df[
        filtered_df["Region"] == selected_region
    ]

if selected_category != "All Categories":
    filtered_df = filtered_df[
        filtered_df["Product_Category"] == selected_category
    ]

if selected_year != "All Years":
    filtered_df = filtered_df[
        filtered_df["Year"] == selected_year
    ]

if selected_segment != "All Segments":
    filtered_df = filtered_df[
        filtered_df["Customer_Segment"] == selected_segment
    ]


# --------------------------------------------------
# SELECTED FILTER SUMMARY
# --------------------------------------------------

st.info(
    f"Country: **{selected_country}**  |  "
    f"Region: **{selected_region}**  |  "
    f"Category: **{selected_category}**  |  "
    f"Year: **{selected_year}**  |  "
    f"Segment: **{selected_segment}**"
)


# --------------------------------------------------
# HANDLE EMPTY RESULTS
# --------------------------------------------------

if filtered_df.empty:

    st.warning(
        "No records found for the selected filters. "
        "Please choose different filters."
    )

    st.stop()


# --------------------------------------------------
# KPI CALCULATIONS
# --------------------------------------------------

total_sales = filtered_df["Total_Sales"].sum()

total_profit = filtered_df["Profit"].sum()

total_orders = filtered_df["Order_ID"].nunique()

total_quantity = filtered_df["Quantity"].sum()

average_order_value = (
    total_sales / total_orders
    if total_orders > 0
    else 0
)

profit_margin = (
    (total_profit / total_sales) * 100
    if total_sales != 0
    else 0
)


# --------------------------------------------------
# KPI DISPLAY
# --------------------------------------------------

st.subheader("📈 Business KPIs")

col1, col2, col3 = st.columns(3)

col1.metric(
    "Total Sales",
    f"{total_sales:,.2f}"
)

col2.metric(
    "Total Profit",
    f"{total_profit:,.2f}"
)

col3.metric(
    "Total Orders",
    f"{total_orders:,}"
)


col4, col5, col6 = st.columns(3)

col4.metric(
    "Quantity Sold",
    f"{total_quantity:,}"
)

col5.metric(
    "Average Order Value",
    f"{average_order_value:,.2f}"
)

col6.metric(
    "Profit Margin",
    f"{profit_margin:.2f}%"
)


st.divider()


# --------------------------------------------------
# MONTHLY SALES TREND
# --------------------------------------------------

st.subheader("📈 Monthly Sales Trend")

monthly_sales = (
    filtered_df
    .groupby(
        ["Year", "Month_Number", "Month"],
        as_index=False
    )["Total_Sales"]
    .sum()
    .sort_values(
        ["Year", "Month_Number"]
    )
)

monthly_sales["Year-Month"] = (
    monthly_sales["Year"].astype(str)
    + "-"
    + monthly_sales["Month"]
)

fig_monthly = px.line(
    monthly_sales,
    x="Year-Month",
    y="Total_Sales",
    markers=True,
    title="Monthly Sales Trend"
)

fig_monthly.update_layout(
    xaxis_title="Month",
    yaxis_title="Sales",
    hovermode="x unified"
)

st.plotly_chart(
    fig_monthly,
    use_container_width=True
)


# --------------------------------------------------
# CATEGORY ANALYSIS
# --------------------------------------------------

st.subheader("🛍️ Category Analysis")

category_data = (
    filtered_df
    .groupby(
        "Product_Category",
        as_index=False
    )
    .agg(
        Sales=("Total_Sales", "sum"),
        Profit=("Profit", "sum"),
        Quantity=("Quantity", "sum")
    )
    .sort_values(
        "Sales",
        ascending=False
    )
)

col1, col2 = st.columns(2)

with col1:

    fig_category_sales = px.bar(
        category_data,
        x="Product_Category",
        y="Sales",
        title="Sales by Category",
        text_auto=".2s"
    )

    st.plotly_chart(
        fig_category_sales,
        use_container_width=True
    )


with col2:

    fig_category_profit = px.bar(
        category_data,
        x="Product_Category",
        y="Profit",
        title="Profit by Category",
        text_auto=".2s"
    )

    st.plotly_chart(
        fig_category_profit,
        use_container_width=True
    )


# --------------------------------------------------
# COUNTRY ANALYSIS
# --------------------------------------------------

st.subheader("🌍 Country Analysis")

country_data = (
    filtered_df
    .groupby(
        "Country",
        as_index=False
    )
    .agg(
        Sales=("Total_Sales", "sum"),
        Profit=("Profit", "sum"),
        Orders=("Order_ID", "nunique")
    )
    .sort_values(
        "Sales",
        ascending=False
    )
)

col1, col2 = st.columns(2)

with col1:

    fig_country_sales = px.bar(
        country_data,
        x="Country",
        y="Sales",
        title="Sales by Country",
        text_auto=".2s"
    )

    st.plotly_chart(
        fig_country_sales,
        use_container_width=True
    )


with col2:

    fig_country_profit = px.bar(
        country_data,
        x="Country",
        y="Profit",
        title="Profit by Country",
        text_auto=".2s"
    )

    st.plotly_chart(
        fig_country_profit,
        use_container_width=True
    )


# --------------------------------------------------
# REGION ANALYSIS
# --------------------------------------------------

st.subheader("🌎 Regional Analysis")

region_data = (
    filtered_df
    .groupby(
        "Region",
        as_index=False
    )
    .agg(
        Sales=("Total_Sales", "sum"),
        Profit=("Profit", "sum"),
        Orders=("Order_ID", "nunique")
    )
    .sort_values(
        "Sales",
        ascending=False
    )
)

col1, col2 = st.columns(2)

with col1:

    fig_region_sales = px.bar(
        region_data,
        x="Region",
        y="Sales",
        title="Sales by Region",
        text_auto=".2s"
    )

    st.plotly_chart(
        fig_region_sales,
        use_container_width=True
    )


with col2:

    fig_region_profit = px.bar(
        region_data,
        x="Region",
        y="Profit",
        title="Profit by Region",
        text_auto=".2s"
    )

    st.plotly_chart(
        fig_region_profit,
        use_container_width=True
    )


# --------------------------------------------------
# TOP 10 PRODUCTS
# --------------------------------------------------

st.subheader("🏆 Top 10 Products")

top_products = (
    filtered_df
    .groupby(
        "Product_Name",
        as_index=False
    )
    .agg(
        Sales=("Total_Sales", "sum"),
        Profit=("Profit", "sum"),
        Quantity=("Quantity", "sum")
    )
    .sort_values(
        "Sales",
        ascending=False
    )
    .head(10)
)

fig_products = px.bar(
    top_products.sort_values("Sales"),
    x="Sales",
    y="Product_Name",
    orientation="h",
    title="Top 10 Products by Sales",
    text_auto=".2s"
)

st.plotly_chart(
    fig_products,
    use_container_width=True
)


st.subheader("📋 Top Products Details")

st.dataframe(
    top_products,
    use_container_width=True
)


# --------------------------------------------------
# FILTERED DATASET
# --------------------------------------------------

st.subheader("📊 Filtered Dataset")

st.write(
    f"Showing **{len(filtered_df):,}** records after applying filters."
)

st.dataframe(
    filtered_df.head(100),
    use_container_width=True
)


# --------------------------------------------------
# DOWNLOAD
# --------------------------------------------------

st.subheader("📥 Download Data")

csv_data = filtered_df.to_csv(
    index=False
).encode("utf-8")

st.download_button(
    label="Download Filtered Dataset",
    data=csv_data,
    file_name="filtered_ecommerce_sales.csv",
    mime="text/csv"
)


# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.divider()

st.caption(
    "E-Commerce Sales and Product Analytics Dashboard | "
    "Built with Python, Pandas, Plotly and Streamlit"
)
