import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from src.dashboard_utils import load_data, get_executive_metrics, get_logistics_metrics, get_freight_metrics

st.set_page_config(
    page_title="Olist Supply Chain Analytics",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    :root {
        --olist-blue: #004B93;
        --olist-green: #00A859;
    }
    
    h1, h2, h3 {
        font-family: 'Inter', sans-serif;
    }
    
    div[data-testid="stMetricValue"] {
        color: var(--olist-blue);
        font-size: 2rem;
        font-weight: 700;
    }
    
    .kpi-card {
        background-color: var(--background-color);
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        border: 1px solid var(--secondary-background-color);
        border-left: 5px solid var(--olist-green);
        margin-bottom: 20px;
    }
    
    .kpi-title {
        color: var(--text-color);
        opacity: 0.8;
        font-size: 14px;
        text-transform: uppercase;
        font-weight: 600;
        margin-bottom: 5px;
    }
    
    .kpi-value {
        color: var(--text-color);
        font-size: 28px;
        font-weight: 800;
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: transparent;
        border-radius: 4px 4px 0px 0px;
        gap: 1px;
        padding-top: 10px;
        padding-bottom: 10px;
    }
    .stTabs [aria-selected="true"] {
        border-bottom: 3px solid var(--olist-blue);
        color: var(--olist-blue) !important;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

df_original = load_data()

if df_original.empty:
    st.stop()

st.sidebar.title("Filters")

states = ['All'] + sorted(list(df_original['customer_state'].dropna().unique()))
selected_state = st.sidebar.selectbox("Customer State", states)

categories = ['All'] + sorted(list(df_original['product_category'].dropna().unique()))
selected_category = st.sidebar.selectbox("Product Category", categories)

df = df_original.copy()
if selected_state != 'All':
    df = df[df['customer_state'] == selected_state]
if selected_category != 'All':
    df = df[df['product_category'] == selected_category]

st.title("Olist Operations & Product Analytics")
st.markdown("A deep dive into operational efficiency, product ratings, and customer purchasing behavior.")

total_rev, total_orders, total_customers, avg_order_value = get_executive_metrics(df)
avg_seller_proc, avg_carrier_transit, late_pct, valid_logs = get_logistics_metrics(df)
avg_freight, avg_freight_ratio = get_freight_metrics(df)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f'<div class="kpi-card"><div class="kpi-title">Total Revenue</div><div class="kpi-value">R$ {total_rev:,.0f}</div></div>', unsafe_allow_html=True)
with col2:
    st.markdown(f'<div class="kpi-card"><div class="kpi-title">Total Orders</div><div class="kpi-value">{total_orders:,}</div></div>', unsafe_allow_html=True)
with col3:
    st.markdown(f'<div class="kpi-card"><div class="kpi-title">Avg Order Value</div><div class="kpi-value">R$ {avg_order_value:.2f}</div></div>', unsafe_allow_html=True)
with col4:
    st.markdown(f'<div class="kpi-card"><div class="kpi-title">Late Delivery Rate</div><div class="kpi-value">{late_pct:.1f}%</div></div>', unsafe_allow_html=True)

tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Executive", "🚚 Logistics", "📦 Products", "⭐ Ratings & Payments", "💡 Recommendations"])

olist_blue = '#004B93'
olist_green = '#00A859'
color_discrete_sequence = ['#004B93', '#00A859', '#F9A01B', '#E53935', '#8E24AA', '#03A9F4', '#FF9800', '#4CAF50']

with tab1:
    st.header("Executive Overview & Purchasing Patterns")
    
    col_a, col_b = st.columns(2)
    with col_a:
        monthly_sales = df.groupby('order_month')['price'].sum().reset_index()
        fig_revenue = px.line(monthly_sales, x='order_month', y='price', 
                              title="Total Monthly Revenue Trends",
                              template="plotly_white", line_shape='spline')
        fig_revenue.update_traces(line_color=olist_blue, line_width=3)
        st.plotly_chart(fig_revenue, use_container_width=True)
        
    with col_b:
        state_counts = df['customer_state'].value_counts().reset_index().head(10)
        state_counts.columns = ['customer_state', 'count']
        fig_state = px.bar(state_counts, x='customer_state', y='count', 
                           title="Top 10 States by Order Volume",
                           color_discrete_sequence=[olist_green])
        st.plotly_chart(fig_state, use_container_width=True)

    st.subheader("Order Timing Analysis")
    col_c, col_d = st.columns(2)
    with col_c:
        day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        dow_counts = df['order_day_of_week'].value_counts().reindex(day_order).reset_index()
        dow_counts.columns = ['order_day_of_week', 'count']
        fig_dow = px.bar(dow_counts, x='order_day_of_week', y='count',
                         title="Order Volume by Day of Week",
                         color_discrete_sequence=[olist_blue])
        st.plotly_chart(fig_dow, use_container_width=True)
        
    with col_d:
        hour_counts = df['order_hour'].value_counts().sort_index().reset_index()
        hour_counts.columns = ['order_hour', 'count']
        fig_hour = px.line(hour_counts, x='order_hour', y='count',
                           title="Order Volume by Hour of Day",
                           template="plotly_white", line_shape='spline')
        fig_hour.update_traces(line_color=olist_green, line_width=3)
        fig_hour.update_layout(xaxis=dict(tickmode='linear', tick0=0, dtick=2))
        st.plotly_chart(fig_hour, use_container_width=True)

with tab2:
    st.header("Logistics, Freight Costs & Delivery Performance")
    
    col_e, col_f = st.columns(2)
    
    with col_e:
        state_late = valid_logs.groupby('customer_state')['is_late'].mean().reset_index()
        state_late['is_late'] = state_late['is_late'] * 100
        state_late = state_late.sort_values('is_late', ascending=False)
        fig_late = px.bar(state_late, x='customer_state', y='is_late',
                          title="Late Delivery Rate (%) by Customer State",
                          labels={'is_late': 'Late Rate (%)', 'customer_state': 'State'},
                          color='is_late', color_continuous_scale='Reds')
        st.plotly_chart(fig_late, use_container_width=True)
        
    with col_f:
        state_logs = valid_logs.groupby('customer_state')[['time_to_ship', 'carrier_time']].mean().sort_values('carrier_time', ascending=False).reset_index()
        fig_stack = go.Figure(data=[
            go.Bar(name='Seller Processing', x=state_logs['customer_state'], y=state_logs['time_to_ship'], marker_color=olist_blue),
            go.Bar(name='Carrier Transit', x=state_logs['customer_state'], y=state_logs['carrier_time'], marker_color=olist_green)
        ])
        fig_stack.update_layout(barmode='stack', title="Delivery Bottlenecks: Seller vs. Carrier by State", xaxis_title="State", yaxis_title="Average Days")
        st.plotly_chart(fig_stack, use_container_width=True)

    st.subheader("Freight Cost Analysis")
    col_g, col_h = st.columns(2)
    
    with col_g:
        state_freight = df.groupby('customer_state')['freight_ratio'].mean().reset_index().sort_values('freight_ratio', ascending=False)
        fig_freight = px.bar(state_freight, x='customer_state', y='freight_ratio',
                             title="Freight as a % of Product Price by State",
                             labels={'freight_ratio': 'Freight % of Price', 'customer_state': 'State'},
                             color_discrete_sequence=['#F9A01B'])
        st.plotly_chart(fig_freight, use_container_width=True)

    with col_h:
        seller_state_time = valid_logs.groupby('seller_state')['time_to_ship'].mean().reset_index().sort_values('time_to_ship', ascending=False)
        fig_seller = px.bar(seller_state_time, x='seller_state', y='time_to_ship',
                            title="Average Seller Processing Time by Seller State",
                            labels={'time_to_ship': 'Avg Processing Days', 'seller_state': 'Seller State'},
                            color_discrete_sequence=['#8E24AA'])
        st.plotly_chart(fig_seller, use_container_width=True)

with tab3:
    st.header("Product Category Insights")
    
    col_i, col_j = st.columns(2)
    
    with col_i:
        cat_counts = df['product_category'].value_counts().reset_index().head(10)
        cat_counts.columns = ['category', 'sales_volume']
        fig_cat = px.pie(cat_counts, values='sales_volume', names='category', hole=0.4,
                         title="Volume Breakdown (Top 10 Categories)", 
                         color_discrete_sequence=color_discrete_sequence)
        st.plotly_chart(fig_cat, use_container_width=True)
        
    with col_j:
        cat_revenue = df.groupby('product_category')['price'].sum().reset_index().sort_values('price', ascending=False).head(10)
        fig_cat_rev = px.bar(cat_revenue, x='price', y='product_category', orientation='h',
                             title="Revenue by Top Categories",
                             color_discrete_sequence=[olist_blue])
        fig_cat_rev.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_cat_rev, use_container_width=True)

with tab4:
    st.header("Product Ratings & Payments Analysis")
    
    col_k, col_l = st.columns(2)
    
    with col_k:
        if 'review_score' in df.columns and not df['review_score'].isna().all():
            cat_ratings = df.groupby('product_category').agg(
                avg_rating=('review_score', 'mean'),
                volume=('order_id', 'count')
            ).reset_index()
            cat_ratings = cat_ratings[cat_ratings['volume'] > 50] # Filter low volume
            
            top_rated = cat_ratings.sort_values('avg_rating', ascending=False).head(5)
            worst_rated = cat_ratings.sort_values('avg_rating', ascending=True).head(5)
            
            combined_ratings = pd.concat([top_rated, worst_rated]).sort_values('avg_rating', ascending=True)
            combined_ratings['Type'] = np.where(combined_ratings['avg_rating'] >= combined_ratings['avg_rating'].median(), 'Top Rated', 'Worst Rated')
            
            fig_ratings = px.bar(combined_ratings, x='avg_rating', y='product_category', orientation='h',
                                 title="Best vs Worst Rated Categories (Min. 50 Orders)",
                                 color='Type', color_discrete_map={'Top Rated': '#4CAF50', 'Worst Rated': '#F44336'})
            fig_ratings.update_layout(xaxis=dict(range=[1, 5]))
            st.plotly_chart(fig_ratings, use_container_width=True)
        else:
            st.info("Review scores not available for the selected filters.")
            
    with col_l:
        if 'payment_type' in df.columns and not df['payment_type'].isna().all():
            pay_counts = df['payment_type'].value_counts().reset_index()
            pay_counts.columns = ['payment_type', 'count']
            
            fig_pay = px.pie(pay_counts, values='count', names='payment_type', hole=0.3,
                             title="Payment Method Distribution",
                             color_discrete_sequence=px.colors.qualitative.Pastel)
            st.plotly_chart(fig_pay, use_container_width=True)
        else:
            st.info("Payment types not available for the selected filters.")

with tab5:
    st.header("Key Business Insights & Strategic Recommendations")
    st.markdown("""
    Based on our comprehensive operational and product analysis, here are the detailed findings and recommendations:
    
    ### 1. Delivery Performance & Logistics Bottlenecks
    - **Insight**: Northern (e.g., RR, AP, AM) and Northeastern states suffer from extremely high late delivery rates. The stacked bar chart reveals this is primarily due to *carrier transit times*.
    - **Recommendation**: Olist must diversify its carrier portfolio in the North/Northeast. Establish partnerships with specialized regional couriers and consider implementing intermediate cross-docking hubs closer to these high-delay regions.
    
    ### 2. Freight Cost Optimization
    - **Insight**: In remote states, freight costs account for a massive percentage of the product price (often >30%), acting as a significant deterrent to conversion rates.
    - **Recommendation**: Implement a dynamic pricing strategy. For high-margin, lightweight categories, Olist should absorb a portion of the freight cost to offer "Free Shipping" tiers, driving conversion where shipping shock causes cart abandonment.
    
    ### 3. Seller Performance Management
    - **Insight**: Seller processing times are highly inconsistent by state. Sellers in certain regions take an average of 4-5 days simply to hand over the product to the carrier.
    - **Recommendation**: Introduce a "Fast Dispatch" badge for sellers who consistently hand over items within 24-48 hours. Time-to-ship must become a core metric for seller ranking algorithms.
    
    ### 4. Product Quality & Ratings Intervention
    - **Insight**: Certain categories consistently rank in the "Worst Rated" chart (e.g., office furniture, security/services). These categories often suffer from either misleading descriptions or shipping damage.
    - **Recommendation**: Launch a Quality Assurance intervention for the bottom 5 categories. Require mandatory, clearer product dimensions and high-quality images from sellers in these categories to manage customer expectations and reduce negative reviews.
    
    ### 5. Payment Methods
    - **Insight**: Credit Cards dominate the payment landscape, but Boletos still make up a significant portion of transactions. Boletos generally have longer payment confirmation times which delays the seller's dispatch time.
    - **Recommendation**: Incentivize credit card or PIX/instant payments over Boleto by offering a 2-3% discount at checkout. This will accelerate the entire order lifecycle and reduce the "time to ship" bottleneck.
    """)

