import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

# Load the saved clean dataset
try:
    data = pd.read_csv('south_asia_cleaned_data.csv')
except FileNotFoundError:
    st.error("❌ 'south_asia_cleaned_data.csv' not found. Please verify the file path.")
    st.stop()

# Set dashboard configuration with wide layout and custom title
st.set_page_config(
    page_title="South Asia Intelligence Dashboard", 
    page_icon="📈", 
    layout="wide"
)

# Custom CSS injection to create elegant card structures and custom layouts
st.markdown("""
    <style>
    .metric-card {
        background-color: #1f2635;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #3498db;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.2);
        margin-bottom: 10px;
    }
    .section-header {
        color: #3498db;
        font-family: 'Helvetica Neue', sans-serif;
        font-weight: bold;
        border-bottom: 2px solid #2c3e50;
        padding-bottom: 8px;
        margin-top: 25px;
        margin-bottom: 15px;
    }
    </style>
""", unsafe_allow_html=True)

# --- DATA COMPILATION PIPELINE ---
data = pd.DataFrame(data)
all_countries = sorted(data['Country'].dropna().unique())

# --- SIDEBAR CONTROL PANEL ---
st.sidebar.image("https://img.icons8.com/clouds/100/000000/analytics.png", width=80)
st.sidebar.title("National Intelligence")
st.sidebar.markdown("---")
target_country = st.sidebar.selectbox("🎯 Target Country Profile", all_countries, index=all_countries.index('India') if 'India' in all_countries else 0)

# Filter country specific data chronologically
df_nation = data[data['Country'] == target_country].copy().sort_values(by='Year')

# --- DEFINING EXCLUSION LIST ---
excluded_features = [
    'Gini index',
    'Poverty headcount ratio at $2.15 a day (2017 PPP) (% of population)',
    'Literacy rate, adult total (% of people ages 15 and above)',
    'Research and development expenditure (% of GDP)',
    'High-technology exports (% of manufactured exports)'
]

# Get all column names from the dataframe, ignoring structural ones like Country/Year
all_columns = [col for col in data.columns if col not in ['Country', 'Year']]

# --- MASTER FILTER: Generate list of allowed features for visualization ---
analysis_features = [col for col in all_columns if col not in excluded_features]

# Ensure 'GDP (current US$)' is explicitly tracked for KPI cards if it exists in data
all_conversion_cols = list(set(analysis_features + ['GDP (current US$)', 'Year']))

# Safeguard numeric conversions for the features list
for col in all_conversion_cols:
    if col in data.columns:
        data[col] = pd.to_numeric(data[col], errors='coerce')
        df_nation[col] = pd.to_numeric(df_nation[col], errors='coerce')

# --- DATA EXPORT ACTION (SIDEBAR ENHANCEMENT) ---
csv_data = df_nation.to_csv(index=False).encode('utf-8')
st.sidebar.download_button(
    label="📥 Export Country Data to CSV",
    data=csv_data,
    file_name=f"{target_country}_cleaned_analytics.csv",
    mime="text/csv",
)

# --- MAIN PAGE CORE HEADERS ---
st.markdown(f"<h1 style='color: #ffffff;'>📊 {target_country} Strategic Profile & Performance Analytics</h1>", unsafe_allow_html=True)

# --- 1. POPULATION INTEGRATED SCORECARDS (KPI BLOCK) ---
st.markdown("<div class='section-header'>⚡ Executive Vital Signs (Latest Available Statistics)</div>", unsafe_allow_html=True)

kpi_cols = st.columns(5)

def get_latest_metrics(df, col):
    if col not in df.columns:
        return 0, 0
    valid_data = df[['Year', col]].dropna().sort_values(by='Year')
    if len(valid_data) >= 2:
        latest = valid_data[col].iloc[-1]
        previous = valid_data[col].iloc[-2]
        delta = latest - previous
        return latest, delta
    elif len(valid_data) == 1:
        return valid_data[col].iloc[0], 0
    return 0, 0

# Populating KPI blocks
with kpi_cols[0]:
    pop_val, pop_delta = get_latest_metrics(df_nation, 'Population, total')
    st.metric(label="Total Population", value=f"{pop_val/1e6:,.1f}M", delta=f"{pop_delta/1e6:+,.1f}M")

with kpi_cols[1]:
    val, delta = get_latest_metrics(df_nation, 'GDP per capita (current US$)')
    st.metric(label="GDP Per Capita", value=f"${val:,.2f}", delta=f"${delta:,.2f}")

with kpi_cols[2]:
    val, delta = get_latest_metrics(df_nation, 'Life expectancy at birth, total (years)')
    st.metric(label="Life Expectancy", value=f"{val:.1f} Yrs", delta=f"{delta:.2f} Yrs")

with kpi_cols[3]:
    val, delta = get_latest_metrics(df_nation, 'Individuals using the Internet (% of population)')
    st.metric(label="Internet Penetration", value=f"{val:.1f}%", delta=f"{delta:.1f}%")

with kpi_cols[4]:
    gdp_val, gdp_delta = get_latest_metrics(df_nation, 'GDP (current US$)')
    if gdp_val >= 1e12:
        st.metric(label="Total GDP", value=f"${gdp_val/1e12:,.2f}T", delta=f"${gdp_delta/1e12:,.2f}T")
    else:
        st.metric(label="Total GDP", value=f"${gdp_val/1e9:,.2f}B", delta=f"${gdp_delta/1e9:,.2f}B")

st.markdown("---")

# --- 2. MULTI-TAB MATRIX ARCHITECTURE ---
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📈 Feature Trend Explorer", 
    "🗺️ Geographic Benchmarking", 
    "🔄 Indicator Interactions (Correlation)", 
    "🎯 Automated Strategic Insights",
    "👥 Cross-Country Comparison"
])

# TAB 1: Dynamic Dropdown Feature Explorer
with tab1:
    st.markdown("### Indicator Trend Analysis")
    st.markdown("Select any allowed feature from the dropdown menu to immediately map its timeline profile.")
    
    selected_feature = st.selectbox("🔍 Choose a feature to visualize:", analysis_features)
    
    if selected_feature:
        df_plot = df_nation[['Year', selected_feature]].dropna()
        
        if not df_plot.empty:
            fig_trend = px.line(
                df_plot, x='Year', y=selected_feature, markers=True,
                title=f"Historical Vector for {selected_feature} ({target_country})",
                color_discrete_sequence=['#3498db']
            )
            fig_trend.update_layout(template="plotly_dark", height=500, xaxis={'type': 'category'})
            fig_trend.update_traces(line=dict(width=3), marker=dict(size=8))
            st.plotly_chart(fig_trend, use_container_width=True)
        else:
            st.warning(f"No valid historical data points available to map for '{selected_feature}' in {target_country}.")

# TAB 2: Geographic Benchmarking Map
with tab2:
    st.markdown("### Geographic Regional Context Comparison")
    map_feature = st.selectbox("Select Context Variable to Map", analysis_features, key="map_box")
    
    latest_year = data['Year'].max()
    df_map = data[data['Year'] == latest_year].copy()
    if map_feature in df_map.columns:
        df_map[map_feature] = pd.to_numeric(df_map[map_feature], errors='coerce')
        
        fig_map = px.choropleth(
            df_map, locations="Country", locationmode="country names",
            color=map_feature, scope="asia", color_continuous_scale="Viridis",
            title=f"Regional Comparative Baseline ({latest_year}): {map_feature}"
        )
        fig_map.update_layout(height=600, geo=dict(showframe=False, bgcolor='rgba(0,0,0,0)', projection_type="equirectangular"), template="plotly_dark")
        st.plotly_chart(fig_map, use_container_width=True)

# TAB 3: Matrix Heatmap
with tab3:
    st.markdown("### Statistical Interdependence Matrix")
    
    df_corr = df_nation[analysis_features].apply(pd.to_numeric, errors='coerce')
    corr_matrix = df_corr.corr()
    
    fig_heat = px.imshow(
        corr_matrix, text_auto=".2f", aspect="auto",
        color_continuous_scale="RdBu", color_continuous_midpoint=0
    )
    fig_heat.update_layout(height=700, template="plotly_dark")
    st.plotly_chart(fig_heat, use_container_width=True)

# TAB 4: Strategic Automated Insights & Polished Statistics Table
with tab4:
    st.markdown("### Strategic Data Summary & Matrix Properties")
    
    stats_summary = df_nation[analysis_features].describe().T
    growth_dict = {}
    for col in analysis_features:
        valid_points = df_nation[['Year', col]].dropna().sort_values(by='Year')
        growth_dict[col] = valid_points[col].iloc[-1] - valid_points[col].iloc[0] if len(valid_points) >= 2 else 0
        
    stats_summary['Total Structural Change'] = pd.Series(growth_dict)
    clean_matrix = stats_summary[['mean', 'std', 'min', 'max', 'Total Structural Change']]
    
    # ENHANCEMENT: Clean, human-readable formatting with commas for large numbers
    st.dataframe(
        clean_matrix.style.format(precision=2, thousands=",").background_gradient(cmap='Blues'), 
        use_container_width=True
    )

# TAB 5: Side-by-Side Country Comparison Panel
with tab5:
    st.markdown("### 👥 Bilateral Growth Trajectory Comparison panel")
    st.markdown("Compare the performance metrics of two South Asian nations side-by-side over the historical timeline.")
    
    comp_cols = st.columns(2)
    with comp_cols[0]:
        country_a = st.selectbox("Select Country A:", all_countries, index=all_countries.index(target_country))
    with comp_cols[1]:
        remaining_countries = [c for c in all_countries if c != country_a]
        country_b = st.selectbox("Select Country B to Compare Against:", remaining_countries, index=0)
        
    comparison_feature = st.selectbox("📊 Select Metric to Benchmark:", analysis_features, key="comp_feature_box")
    
    if comparison_feature:
        df_a = data[data['Country'] == country_a][['Year', comparison_feature]].dropna().sort_values(by='Year')
        df_b = data[data['Country'] == country_b][['Year', comparison_feature]].dropna().sort_values(by='Year')
        
        if not df_a.empty or not df_b.empty:
            fig_comp = go.Figure()
            
            # Country A Trace
            fig_comp.add_trace(go.Scatter(
                x=df_a['Year'], y=df_a[comparison_feature],
                name=country_a, mode='lines+markers',
                line=dict(color='#3498db', width=3), marker=dict(size=6)
            ))
            
            # Country B Trace
            fig_comp.add_trace(go.Scatter(
                x=df_b['Year'], y=df_b[comparison_feature],
                name=country_b, mode='lines+markers',
                line=dict(color='#e67e22', width=3), marker=dict(size=6)
            ))
            
            fig_comp.update_layout(
                title=f"{comparison_feature}: {country_a} vs {country_b}",
                template="plotly_dark",
                height=550,
                xaxis={'type': 'category'},
                hovermode="x unified"
            )
            st.plotly_chart(fig_comp, use_container_width=True)
        else:
            st.warning("Insufficient overlapping records found to draw a trajectory line between these two targets.")