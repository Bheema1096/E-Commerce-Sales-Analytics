import streamlit as st
import pandas as pd
import plotly.express as px


# -----------------------------
# PAGE CONFIGURATION
# -----------------------------

st.set_page_config(
    page_title="E-Commerce Sales Analytics",
    page_icon="📊",
    layout="wide"
)


# -----------------------------
# LOAD DATA
# -----------------------------

df = pd.read_csv("dataset/cleaned_ecommerce_sales.csv")

df["Order Date"] = pd.to_datetime(df["Order Date"], errors="coerce")


# -----------------------------
# TITLE
# -----------------------------

st.title("📊 E-Commerce Sales and Product Analytics Dashboard")

st.write(
    "Analyze sales, profit, products, categories, regions, and time-based trends."
)


# -----------------------------
# SIDEBAR FILTERS
# -----------------------------

st.sidebar.header("🔎 Dashboard Filters")

categories = ["All"] + sorted(
    df["Product Category"].dropna().unique().tolist()
)

regions = ["All"] + sorted(
    df["Region"].dropna().unique().tolist()
)

segments = ["All"] + sorted(
    df["Segment"].dropna().unique().tolist()
)


selected_category = st.sidebar.selectbox(
    "Product Category",
    categories
)

selected_region = st.sidebar.selectbox(
    "Region",
    regions
)

selected_segment = st.sidebar.selectbox(
    "Customer Segment",
    segments
)


# -----------------------------
# APPLY FILTERS
# -----------------------------

filtered_df = df.copy()


if selected_category != "All":
    filtered_df = filtered_df[
        filtered_df["Product Category"] == selected_category
    ]


if selected_region != "All":
    filtered_df = filtered_df[
        filtered_df["Region"] == selected_region
    ]


if selected_segment != "All":
    filtered_df = filtered_df[
        filtered_df["Segment"] == selected_segment
    ]


# -----------------------------
# BUSINESS KPIs
# -----------------------------

total_sales = filtered_df["Sales"].sum()

total_profit = filtered_df["Profit"].sum()

total_orders = filtered_df["Order ID"].nunique()

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


# -----------------------------
# MONTHLY SALES TREND
# -----------------------------

st.subheader("📈 Monthly Sales Trend")


monthly_sales = (
    filtered_df
    .groupby(["Year", "Month Number", "Month"], as_index=False)["Sales"]
    .sum()
    .sort_values(["Year", "Month Number"])
)


monthly_sales["Year-Month"] = (
    monthly_sales["Year"].astype(str)
    + "-"
    + monthly_sales["Month"].astype(str)
)


fig_monthly = px.line(
    monthly_sales,
    x="Year-Month",
    y="Sales",
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


# -----------------------------
# CATEGORY ANALYSIS
# -----------------------------

st.subheader("🛍️ Category Analysis")


category_data = (
    filtered_df
    .groupby("Product Category", as_index=False)
    .agg(
        Sales=("Sales", "sum"),
        Profit=("Profit", "sum")
    )
)


col1, col2 = st.columns(2)


with col1:

    fig_category_sales = px.bar(
        category_data,
        x="Product Category",
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
        x="Product Category",
        y="Profit",
        title="Profit by Category",
        text_auto=".2s"
    )

    st.plotly_chart(
        fig_category_profit,
        use_container_width=True
    )


# -----------------------------
# REGIONAL ANALYSIS
# -----------------------------

st.subheader("🌍 Regional Analysis")


region_data = (
    filtered_df
    .groupby("Region", as_index=False)
    .agg(
        Sales=("Sales", "sum"),
        Profit=("Profit", "sum"),
        Orders=("Order ID", "nunique")
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


# -----------------------------
# TOP 10 PRODUCTS
# -----------------------------

st.subheader("🏆 Top 10 Products")


top_products = (
    filtered_df
    .groupby("Product", as_index=False)
    .agg(
        Sales=("Sales", "sum"),
        Profit=("Profit", "sum"),
        Quantity=("Quantity", "sum")
    )
    .sort_values("Sales", ascending=False)
    .head(10)
)


fig_products = px.bar(
    top_products.sort_values("Sales"),
    x="Sales",
    y="Product",
    orientation="h",
    title="Top 10 Products by Sales",
    text_auto=".2s"
)

st.plotly_chart(
    fig_products,
    use_container_width=True
)


# -----------------------------
# PRODUCT TABLE
# -----------------------------

st.subheader("📋 Top Products Details")

st.dataframe(
    top_products,
    use_container_width=True
)


# -----------------------------
# DATA PREVIEW
# -----------------------------

st.subheader("📊 Filtered Dataset")

st.write(
    f"Showing {len(filtered_df):,} records after applying filters."
)

st.dataframe(
    filtered_df.head(100),
    use_container_width=True
)


# -----------------------------
# DOWNLOAD DATA
# -----------------------------

st.subheader("📥 Download Data")


csv_data = filtered_df.to_csv(index=False).encode("utf-8")


st.download_button(
    label="Download Filtered Dataset",
    data=csv_data,
    file_name="filtered_ecommerce_sales.csv",
    mime="text/csv"
)


# -----------------------------
# FOOTER
# -----------------------------

st.divider()

st.caption(
    "E-Commerce Sales and Product Analytics Dashboard | "
    "Built with Python, Pandas, Plotly and Streamlit"
) 