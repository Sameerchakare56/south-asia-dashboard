import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

# Set dashboard configuration with wide layout and custom title
st.set_page_config(
    page_title="South Asia Intelligence Dashboard", 
    page_icon="📈", 
    layout="wide"
)

# Load the saved clean dataset
try:
    data = pd.read_csv('south_asia_cleaned_data.csv')
except FileNotFoundError:
    st.error("❌ 'south_asia_cleaned_data.csv' not found. Please verify the file path.")
    st.stop()

# --- MOBILE ENHANCED CSS INJECTION ---
# Employs media queries to automatically adapt grid items, fonts, and spaces for viewports under 768px
# --- MOBILE ENHANCED MINI-CARD CSS INJECTION ---
# --- ULTRA COMPACT MOBILE INLINE CSS INJECTION ---
st.markdown("""
    <style>
    /* Global Spacing Reductions */
    .reportview-container .main .block-container {
        padding: 0.5rem 0.5rem !important;
    }
    
    /* Clean, Borderless 2-Column Grid */
    .metric-card-container {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 6px;
        margin-bottom: 10px;
    }
    
    /* Flat Single-Row Layout */
    .mobile-metric-card {
        background-color: rgba(31, 38, 53, 0.4);
        padding: 6px 10px;
        border-radius: 6px;
        border-left: 3px solid #3498db;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    
    /* Shrink Header Title Margins */
    h2 {
        margin-top: 0px !important;
        margin-bottom: 5px !important;
        font-size: 1.4rem !important;
    }
    
    .metric-label {
        font-size: 0.65rem;
        color: #8a99ad;
        text-transform: uppercase;
        letter-spacing: 0.2px;
        margin-bottom: 1px;
    }
    
    /* Value & Delta Flex Alignment on same row visually */
    .metric-value {
        font-size: 1.05rem;
        font-weight: 700;
        color: #ffffff;
        display: inline-block;
        margin-right: 5px;
    }
    
    .metric-delta {
        font-size: 0.7rem;
        font-weight: 600;
        display: inline-block;
    }
    
    .delta-pos { color: #2ecc71; }
    .delta-neg { color: #e74c3c; }
    .delta-neu { color: #95a5a6; }

    .section-header {
        color: #3498db;
        font-weight: 700;
        font-size: 0.85rem;
        border-bottom: 1px solid #2c3e50;
        padding-bottom: 2px;
        margin-top: 8px;
        margin-bottom: 8px;
    }
    
    /* Restore classic structure on Desktops */
    @media (min-width: 769px) {
        .metric-card-container {
            grid-template-columns: repeat(5, 1fr);
            gap: 12px;
        }
        .mobile-metric-card { padding: 12px; background: linear-gradient(135deg, #1f2635 0%, #161b26 100%); }
        .metric-label { font-size: 0.8rem; margin-bottom: 4px; }
        .metric-value { font-size: 1.4rem; display: block; }
        .metric-delta { font-size: 0.85rem; display: block; margin-top: 4px; }
        .section-header { font-size: 1.1rem; margin-top: 15px; }
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

all_columns = [col for col in data.columns if col not in ['Country', 'Year']]
analysis_features = [col for col in all_columns if col not in excluded_features]
all_conversion_cols = list(set(analysis_features + ['GDP (current US$)', 'Year']))

for col in all_conversion_cols:
    if col in data.columns:
        data[col] = pd.to_numeric(data[col], errors='coerce')
        df_nation[col] = pd.to_numeric(df_nation[col], errors='coerce')

# --- DATA EXPORT ACTION ---
csv_data = df_nation.to_csv(index=False).encode('utf-8')
st.sidebar.download_button(
    label="📥 Export Country Data to CSV",
    data=csv_data,
    file_name=f"{target_country}_cleaned_analytics.csv",
    mime="text/csv",
)

# --- MAIN PAGE CORE HEADERS ---
st.markdown(f"<h2 style='color: #ffffff; margin-bottom:0;'>📊 {target_country} Profile Dashboard</h2>", unsafe_allow_html=True)

# --- 1. POPULATION INTEGRATED SCORECARDS (RESPONSIVE DIV PIPELINE) ---
st.markdown("<div class='section-header'>⚡(Latest Statistics)</div>", unsafe_allow_html=True)

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

# Extract metrics
pop_val, pop_delta = get_latest_metrics(df_nation, 'Population, total')
gdp_cap_val, gdp_cap_delta = get_latest_metrics(df_nation, 'GDP per capita (current US$)')
life_val, life_delta = get_latest_metrics(df_nation, 'Life expectancy at birth, total (years)')
net_val, net_delta = get_latest_metrics(df_nation, 'Individuals using the Internet (% of population)')
gdp_val, gdp_delta = get_latest_metrics(df_nation, 'GDP (current US$)')

# Helper to format delta classes cleanly
def format_delta_str(val, prefix="", suffix=""):
    if val > 0: return f"<span class='metric-delta delta-pos'>▲ {prefix}{val:,.1f}{suffix}</span>"
    elif val < 0: return f"<span class='metric-delta delta-neg'>▼ {prefix}{abs(val):,.1f}{suffix}</span>"
    return f"<span class='metric-delta delta-neu'>● 0.0</span>"

# Constructing HTML injection layout for auto-adjusting responsive wrap cards
gdp_str = f"${gdp_val/1e12:,.2f}T" if gdp_val >= 1e12 else f"${gdp_val/1e9:,.2f}B"
gdp_del_str = f"{gdp_delta/1e12:+,.2f}T" if gdp_val >= 1e12 else f"{gdp_delta/1e9:+,.2f}B"

cards_html = f"""
<div class='metric-card-container'>
    <div class='mobile-metric-card'>
        <div class='metric-label'>Total Population</div>
        <div class='metric-value'>{pop_val/1e6:,.1f}M</div>
        {format_delta_str(pop_delta/1e6, suffix="M")}
    </div>
    <div class='mobile-metric-card'>
        <div class='metric-label'>GDP Per Capita</div>
        <div class='metric-value'>${gdp_cap_val:,.0f}</div>
        {format_delta_str(gdp_cap_delta, prefix="$")}
    </div>
    <div class='mobile-metric-card'>
        <div class='metric-label'>Life Expectancy</div>
        <div class='metric-value'>{life_val:.1f} Yrs</div>
        {format_delta_str(life_delta, suffix=" Yrs")}
    </div>
    <div class='mobile-metric-card'>
        <div class='metric-label'>Internet Penetration</div>
        <div class='metric-value'>{net_val:.1f}%</div>
        {format_delta_str(net_delta, suffix="%")}
    </div>
    <div class='mobile-metric-card'>
        <div class='metric-label'>Total GDP</div>
        <div class='metric-value'>{gdp_str}</div>
        <span class='metric-delta {"delta-pos" if gdp_delta >= 0 else "delta-neg"}'>
            {"▲" if gdp_delta >= 0 else "▼"} {gdp_del_str.replace("+","").replace("-","")}
        </span>
    </div>
</div>
"""
st.markdown(cards_html, unsafe_allow_html=True)

# --- 2. MULTI-TAB ARCHITECTURE ---
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📈 Trend Explorer", 
    "🗺️ Geo Maps", 
    "🔄 Correlations", 
    "🎯 Summary Analytics",
    "👥 Comparisons"
])

# Adjust heights for mobile screens (400px - 450px keeps everything viewable without clipping)
chart_height = 420

with tab1:
    st.markdown("### Indicator Trend Analysis")
    selected_feature = st.selectbox("🔍 Choose a feature to visualize:", analysis_features)
    
    if selected_feature:
        df_plot = df_nation[['Year', selected_feature]].dropna()
        if not df_plot.empty:
            fig_trend = px.line(
                df_plot, x='Year', y=selected_feature, markers=True,
                title=f"Historical Timeline: {selected_feature}",
                color_discrete_sequence=['#3498db']
            )
            fig_trend.update_layout(
                template="plotly_dark", 
                height=chart_height, 
                xaxis={'type': 'category'},
                margin=dict(l=20, r=20, t=40, b=20)
            )
            fig_trend.update_traces(line=dict(width=3), marker=dict(size=6))
            st.plotly_chart(fig_trend, use_container_width=True)
        else:
            st.warning(f"No valid data points for '{selected_feature}'.")

with tab2:
    st.markdown("### Geographic Regional Context")
    map_feature = st.selectbox("Select Context Variable to Map", analysis_features, key="map_box")
    
    latest_year = data['Year'].max()
    df_map = data[data['Year'] == latest_year].copy()
    if map_feature in df_map.columns:
        df_map[map_feature] = pd.to_numeric(df_map[map_feature], errors='coerce')
        
        fig_map = px.choropleth(
            df_map, locations="Country", locationmode="country names",
            color=map_feature, scope="asia", color_continuous_scale="Viridis",
            title=f"Regional Baseline ({latest_year})"
        )
        fig_map.update_layout(
            height=480, 
            geo=dict(showframe=False, bgcolor='rgba(0,0,0,0)', projection_type="equirectangular"), 
            template="plotly_dark",
            margin=dict(l=0, r=0, t=40, b=0)
        )
        st.plotly_chart(fig_map, use_container_width=True)

with tab3:
    st.markdown("### Interdependence Matrix")
    df_corr = df_nation[analysis_features].apply(pd.to_numeric, errors='coerce')
    corr_matrix = df_corr.corr()
    
    fig_heat = px.imshow(
        corr_matrix, text_auto=".2f", aspect="auto",
        color_continuous_scale="RdBu", color_continuous_midpoint=0
    )
    # Give heatmap slightly larger height to accommodate labels beautifully on mobile touch
    fig_heat.update_layout(height=500, template="plotly_dark", margin=dict(l=40, r=20, t=30, b=30))
    st.plotly_chart(fig_heat, use_container_width=True)

with tab4:
    st.markdown("### Strategic Summary Statistics")
    stats_summary = df_nation[analysis_features].describe().T
    growth_dict = {
        col: (df_nation[['Year', col]].dropna().sort_values(by='Year')[col].iloc[-1] - 
              df_nation[['Year', col]].dropna().sort_values(by='Year')[col].iloc[0] 
              if len(df_nation[['Year', col]].dropna()) >= 2 else 0)
        for col in analysis_features
    }
    stats_summary['Total Structural Change'] = pd.Series(growth_dict)
    clean_matrix = stats_summary[['mean', 'std', 'min', 'max', 'Total Structural Change']]
    
    # Styled block containing fluid container configurations
    st.dataframe(
        clean_matrix.style.format(precision=2, thousands=",").background_gradient(cmap='Blues'), 
        use_container_width=True
    )

with tab5:
    st.markdown("### Bilateral Growth Trajectory")
    
    # Grid column splits stack dynamically to 1-column on mobile web layout
    comp_cols = st.columns(2)
    with comp_cols[0]:
        country_a = st.selectbox("Select Country A:", all_countries, index=all_countries.index(target_country))
    with comp_cols[1]:
        remaining_countries = [c for c in all_countries if c != country_a]
        country_b = st.selectbox("Select Country B:", remaining_countries, index=0)
        
    comparison_feature = st.selectbox("📊 Select Metric to Benchmark:", analysis_features, key="comp_feature_box")
    
    if comparison_feature:
        df_a = data[data['Country'] == country_a][['Year', comparison_feature]].dropna().sort_values(by='Year')
        df_b = data[data['Country'] == country_b][['Year', comparison_feature]].dropna().sort_values(by='Year')
        
        if not df_a.empty or not df_b.empty:
            fig_comp = go.Figure()
            
            fig_comp.add_trace(go.Scatter(
                x=df_a['Year'], y=df_a[comparison_feature], name=country_a, mode='lines+markers',
                line=dict(color='#3498db', width=3), marker=dict(size=6)
            ))
            fig_comp.add_trace(go.Scatter(
                x=df_b['Year'], y=df_b[comparison_feature], name=country_b, mode='lines+markers',
                line=dict(color='#e67e22', width=3), marker=dict(size=6)
            ))
            
            fig_comp.update_layout(
                title=f"{country_a} vs {country_b}",
                template="plotly_dark",
                height=chart_height,
                xaxis={'type': 'category'},
                hovermode="x unified",
                margin=dict(l=20, r=20, t=40, b=20),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            st.plotly_chart(fig_comp, use_container_width=True)
        else:
            st.warning("Insufficient overlapping records found.")