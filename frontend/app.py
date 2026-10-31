
import streamlit as st
import requests
import pandas as pd
import altair as alt

API_URL = "http://127.0.0.1:8000"


# =====================================================
# PAGE CONFIGURATION
# =====================================================

st.set_page_config(
    page_title="AI Business Intelligence",
    page_icon="📊",
    layout="wide"
)


# =====================================================
# HEADER
# =====================================================

st.title("📊 AI Business Intelligence Assistant")

st.caption(
    "Explore sales performance, discover business insights, "
    "and ask questions using natural language."
)

st.divider()


# =====================================================
# DASHBOARD DATA FETCHING
# =====================================================

@st.cache_data(ttl=30)
def fetch_dashboard(region=None, product=None):

    params = {}

    if region != "All":
        params["region"] = region

    if product != "All":
        params["product"] = product

    response = requests.get(
        f"{API_URL}/dashboard",
        params=params,
        timeout=10
    )

    response.raise_for_status()

    return response.json()["dashboard"]


# =====================================================
# FILTER OPTIONS
# =====================================================

REGIONS = [
    "All",
    "East",
    "North",
    "South",
    "West"
]

PRODUCTS = [
    "All",
    "Desk",
    "Keyboard",
    "Laptop Stand",
    "Monitor",
    "Office Chair",
    "USB-C Hub",
    "Wireless Mouse"
]


# =====================================================
# INTERACTIVE FILTERS
# =====================================================

st.subheader("🎯 Filter Business Data")

if st.button("↩️ Reset Filters"):

    st.session_state["region_filter"] = "All"
    st.session_state["product_filter"] = "All"


filter_col1, filter_col2 = st.columns(2)

with filter_col1:

    selected_region = st.selectbox(
        "Select Region",
        REGIONS,
        key="region_filter"
    )


with filter_col2:

    selected_product = st.selectbox(
        "Select Product",
        PRODUCTS,
        key="product_filter"
    )


# =====================================================
# LOAD FILTERED DASHBOARD
# =====================================================

try:

    dashboard = fetch_dashboard(
        selected_region,
        selected_product
    )

except requests.exceptions.RequestException:

    st.error(
        "Cannot connect to the backend. "
        "Please make sure FastAPI is running."
    )

    st.stop()


# =====================================================
# KPI CARDS
# =====================================================

st.divider()
st.subheader("📊 Business Overview")

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Total Revenue",
    f"₹{dashboard['total_revenue']:,.0f}"
)

col2.metric(
    "Valid Transactions",
    dashboard["total_transactions"]
)

col3.metric(
    "Average Order Value",
    f"₹{dashboard['average_order_value']:,.2f}"
)

col4.metric(
    "Top Product",
    dashboard["top_product"]["name"]
    if dashboard["top_product"] else "N/A"
)


# =====================================================
# EMPTY RESULT HANDLING
# =====================================================

if dashboard["total_transactions"] == 0:

    st.warning(
        "No matching transactions found for the selected filters. "
        "Try changing the region or product."
    )


# =====================================================
# MONTHLY REVENUE CHART
# =====================================================

st.divider()
st.subheader("📈 Monthly Revenue Trend")

MONTH_NAMES = {
    "01": "January",
    "02": "February",
    "03": "March",
    "04": "April",
    "05": "May",
    "06": "June",
    "07": "July",
    "08": "August",
    "09": "September",
    "10": "October",
    "11": "November",
    "12": "December"
}

monthly_df = pd.DataFrame(
    dashboard["monthly_revenue"]
)

if not monthly_df.empty:

    monthly_df["month_number"] = (
        monthly_df["month"].astype(int)
    )

    monthly_df["month_name"] = (
        monthly_df["month"].map(
            lambda month: MONTH_NAMES.get(month, month)
        )
    )

    monthly_chart = alt.Chart(monthly_df).mark_line(
        point=True
    ).encode(

        x=alt.X(
            "month_name:N",
            sort=alt.SortField(
                field="month_number",
                order="ascending"
            ),
            title="Month"
        ),

        y=alt.Y(
            "revenue:Q",
            scale=alt.Scale(domainMin=0),
            title="Revenue (₹)"
        ),

        tooltip=[
            "month_name",
            "revenue"
        ]

    ).properties(
        height=350
    )

    st.altair_chart(
        monthly_chart,
        use_container_width=True
    )

else:

    st.info("No monthly revenue data available.")


# =====================================================
# REGIONAL AND PRODUCT ANALYTICS
# =====================================================

col1, col2 = st.columns(2)


# -------------------------------
# Regional Revenue
# -------------------------------

with col1:

    st.subheader("🌍 Revenue by Region")

    region_df = pd.DataFrame(
        dashboard["region_revenue"]
    )

    if not region_df.empty:

        region_chart = alt.Chart(
            region_df
        ).mark_bar().encode(

            x=alt.X(
                "region:N",
                sort="-y",
                title="Region"
            ),

            y=alt.Y(
                "revenue:Q",
                scale=alt.Scale(domainMin=0),
                title="Revenue (₹)"
            ),

            tooltip=[
                "region",
                "revenue"
            ]

        ).properties(
            height=350
        )

        st.altair_chart(
            region_chart,
            use_container_width=True
        )

    else:

        st.info("No regional data available.")


# -------------------------------
# Product Revenue
# -------------------------------

with col2:

    st.subheader("📦 Revenue by Product")

    product_df = pd.DataFrame(
        dashboard["product_revenue"]
    )

    if not product_df.empty:

        product_chart = alt.Chart(
            product_df
        ).mark_bar().encode(

            x=alt.X(
                "product:N",
                sort="-y",
                title="Product"
            ),

            y=alt.Y(
                "revenue:Q",
                scale=alt.Scale(domainMin=0),
                title="Revenue (₹)"
            ),

            tooltip=[
                "product",
                "revenue"
            ]

        ).properties(
            height=350
        )

        st.altair_chart(
            product_chart,
            use_container_width=True
        )

    else:

        st.info("No product data available.")


# =====================================================
# BUSINESS HIGHLIGHTS
# =====================================================

st.divider()
st.subheader("🏆 Business Highlights")

col1, col2 = st.columns(2)


with col1:

    if dashboard["top_product"]:

        st.success(
            f"Top Product: {dashboard['top_product']['name']}"
        )

        st.write(
            f"Revenue: ₹{dashboard['top_product']['revenue']:,.2f}"
        )

    else:

        st.info("No top product available.")


with col2:

    if dashboard["top_region"]:

        st.success(
            f"Top Region: {dashboard['top_region']['name']}"
        )

        st.write(
            f"Revenue: ₹{dashboard['top_region']['revenue']:,.2f}"
        )

    else:

        st.info("No top region available.")


# =====================================================
# AI BUSINESS ASSISTANT
# =====================================================

st.divider()

st.header("🤖 Ask Your Business Data")

st.write(
    "Ask questions about revenue, products, regions, "
    "monthly performance, or compare two months."
)

question = st.text_input(
    "Your question",
    placeholder="Example: Which product generated the highest revenue?"
)

if st.button("Analyze Question", type="primary"):

    if not question.strip():

        st.warning("Please enter a question.")

    else:

        try:

            with st.spinner("AI is analyzing your question..."):

                response = requests.post(
                    f"{API_URL}/ask",
                    json={
                        "question": question
                    },
                    timeout=120
                )

            response.raise_for_status()

            result = response.json()

            if result["success"]:

                st.success(result["answer"])

                st.subheader("Supporting Data")

                st.json(
                    result["supporting_data"]
                )

            else:

                st.warning(result["answer"])


        except requests.exceptions.Timeout:

            st.error(
                "The AI request timed out. Please try again."
            )

        except requests.exceptions.RequestException:

            st.error(
                "Could not connect to the AI backend."
            )

        except (ValueError, KeyError):

            st.error(
                "The backend returned an unexpected response."
            )


# =====================================================
# DATA QUALITY MONITORING
# =====================================================

st.divider()

st.header("🔍 Data Quality Monitoring")

if st.button("Run Data Quality Check"):

    try:

        with st.spinner("Validating sales data..."):

            response = requests.get(
                f"{API_URL}/data-quality",
                timeout=15
            )

        response.raise_for_status()

        report = response.json()["validation_report"]


        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Total CSV Records",
            report["total_records"]
        )

        col2.metric(
            "Schema Valid",
            "Yes" if report["schema_valid"] else "No"
        )

        col3.metric(
            "Data Quality",
            "Passed"
            if report["data_quality_passed"]
            else "Issues Found"
        )


        if report["data_quality_passed"]:

            st.success(
                "All data-quality checks passed."
            )

        else:

            st.warning(
                "Data-quality issues were detected. "
                "Review the report below."
            )


        st.subheader("Detailed Validation Report")

        st.json(report)


    except requests.exceptions.RequestException:

        st.error(
            "Could not retrieve the data-quality report."
        )

    except (ValueError, KeyError):

        st.error(
            "The backend returned an unexpected response."
        )
