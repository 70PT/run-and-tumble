import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import ast
import numpy as np

# Set page configuration
st.set_page_config(page_title="Cell Growth Analysis", layout="wide")

st.title("📊 Cell Growth Analysis Dashboard")
st.markdown("Upload your processed data CSV to visualize morphology, growth rates, precipitation, and growth curves interactively.")

# ---------------------------------------------------------
# 1. FILE UPLOAD
# ---------------------------------------------------------
uploaded_file = st.file_uploader("Upload CSV File", type=["csv"])

if uploaded_file is not None:
    try:
        # Load data
        df = pd.read_csv(uploaded_file)
        
        # ---------------------------------------------------------
        # 2. DATA PREPROCESSING
        # ---------------------------------------------------------
        with st.spinner("Processing data..."):
            # List of columns that need parsing from string to list
            list_cols = ['Time after seeding', 'Cell count', 'Morphology', 'Precipitation']
            
            # Parse list columns safely
            for col in list_cols:
                if col in df.columns and isinstance(df[col].iloc[0], str):
                    df[col] = df[col].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else x)

            # --- TRUNCATION LOGIC ---
            # 1. Ensure intra-row consistency: Truncate lists within a row to the shortest list length in that row
            def truncate_row_lists(row):
                # Find min length among the 4 list columns
                lengths = [len(row[col]) for col in list_cols if isinstance(row[col], list)]
                if not lengths: return row
                min_len = min(lengths)
                
                # Truncate each list to min_len
                for col in list_cols:
                    if isinstance(row[col], list):
                        row[col] = row[col][:min_len]
                return row

            df = df.apply(truncate_row_lists, axis=1)

            # 2. Ensure intra-condition consistency: Truncate all replicates in a condition to the shortest length
            # This prevents "tails" where only 1 replicate exists from skewing the average.
            
            truncated_rows = []
            
            for condition, group in df.groupby('Condition'):
                # Find the minimum number of timepoints across all replicates for this condition
                min_points = group['Time after seeding'].apply(len).min()
                
                for _, row in group.iterrows():
                    # Truncate all list columns to this minimum length
                    for col in list_cols:
                        if isinstance(row[col], list):
                            row[col] = row[col][:min_points]
                    truncated_rows.append(row)
            
            df = pd.DataFrame(truncated_rows)

            # --- CREATE LONG DATAFRAME ---
            # "Explode" the lists so we have one row per time point per replicate
            temp_data = {
                'Condition': [], 
                'Time': [], 
                'Cell Count': [],
                'Morphology': [],
                'Precipitation': []
            }
            
            for index, row in df.iterrows():
                cond = row['Condition']
                times = row['Time after seeding']
                counts = row['Cell count']
                morphs = row['Morphology']
                precips = row['Precipitation']
                
                num_points = len(times)
                
                temp_data['Condition'].extend([cond] * num_points)
                temp_data['Time'].extend(times)
                temp_data['Cell Count'].extend(counts)
                temp_data['Morphology'].extend(morphs)
                temp_data['Precipitation'].extend(precips)
            
            df_long = pd.DataFrame(temp_data)
            
            # Round Time to group nearby timepoints (anchoring them to a common integer/half-integer)
            df_long['Time_Rounded'] = df_long['Time'].round(0)

        # ---------------------------------------------------------
        # 3. SIDEBAR - GLOBAL FILTERS
        # ---------------------------------------------------------
        st.sidebar.header("Visualization Settings")
        
        all_conditions = sorted(df['Condition'].unique())
        
        # Multiselect widget
        selected_conditions = st.sidebar.multiselect(
            "Select Conditions to Visualize:",
            options=all_conditions,
            default=all_conditions[:min(5, len(all_conditions))]
        )
        
        if not selected_conditions:
            st.warning("Please select at least one condition in the sidebar to view the plots.")
            st.stop()

        # Filter data based on selection
        filtered_df = df[df['Condition'].isin(selected_conditions)]
        filtered_df_long = df_long[df_long['Condition'].isin(selected_conditions)]

        # ---------------------------------------------------------
        # 4. AGGREGATION
        # ---------------------------------------------------------
        # A. Stats for Bar Charts
        bar_stats = filtered_df.groupby('Condition')[['Average morphology', 'Growth rate (k)', 'Average precipitation']].agg(['mean', 'std']).reset_index()
        bar_stats.columns = ['Condition', 'Morphology_Mean', 'Morphology_Std', 
                             'GrowthRate_Mean', 'GrowthRate_Std', 
                             'Precipitation_Mean', 'Precipitation_Std']

        # B. Stats for Curves (Mean + Std per Condition per Timepoint)
        curve_stats = filtered_df_long.groupby(['Condition', 'Time_Rounded'])[['Cell Count', 'Morphology', 'Precipitation']].agg(['mean', 'std']).reset_index()

        # ---------------------------------------------------------
        # 5. PLOTTING FUNCTION
        # ---------------------------------------------------------
        # Helper to create standard curve plots with shaded error bars
        def create_curve_plot(stats_df, y_col_mean, y_col_std, y_label, title):
            fig = go.Figure()
            palette = px.colors.qualitative.Plotly
            
            conditions = sorted(stats_df['Condition'].unique())
            
            for idx, condition in enumerate(conditions):
                cond_data = stats_df[stats_df['Condition'] == condition].sort_values('Time_Rounded')
                if cond_data.empty: continue

                x = cond_data['Time_Rounded']
                y = cond_data[y_col_mean]
                std = cond_data[y_col_std].fillna(0)
                y_upper = y + std
                y_lower = y - std
                
                color = palette[idx % len(palette)]
                
                # Shaded Area (Std Dev)
                fig.add_trace(go.Scatter(
                    x=pd.concat([x, x[::-1]]),
                    y=pd.concat([y_upper, y_lower[::-1]]),
                    fill='toself',
                    fillcolor=color,
                    opacity=0.15,
                    line=dict(color='rgba(255,255,255,0)'),
                    hoverinfo="skip",
                    showlegend=False,
                    name=f"{condition} Std"
                ))

                # Main Line
                fig.add_trace(go.Scatter(
                    x=x, y=y,
                    mode='lines+markers',
                    name=condition,
                    line=dict(color=color, width=2),
                    marker=dict(size=5)
                ))

            fig.update_layout(
                title=title,
                xaxis_title="Time after seeding (Hours)",
                yaxis_title=y_label,
                template="plotly_white",
                hovermode="x unified",
                legend=dict(title="Condition")
            )
            return fig

        # ---------------------------------------------------------
        # 6. DISPLAY PLOTS
        # ---------------------------------------------------------
        
        # --- ROW 1: BAR CHARTS ---
        st.subheader("Summary Statistics")
        col1, col2, col3 = st.columns(3)

        with col1:
            fig_morph = px.bar(bar_stats, x='Condition', y='Morphology_Mean', error_y='Morphology_Std', 
                               color='Condition', title="Avg Morphology") # Removed template="plotly_white"
            fig_morph.update_layout(showlegend=False, xaxis_title=None)
            st.plotly_chart(fig_morph, use_container_width=True)

        with col2:
            fig_growth = px.bar(bar_stats, x='Condition', y='GrowthRate_Mean', error_y='GrowthRate_Std', 
                                color='Condition', title="Avg Growth Rate (k)") # Removed template="plotly_white"
            fig_growth.update_layout(showlegend=False, xaxis_title=None)
            st.plotly_chart(fig_growth, use_container_width=True)

        with col3:
            fig_precip = px.bar(bar_stats, x='Condition', y='Precipitation_Mean', error_y='Precipitation_Std', 
                                color='Condition', title="Avg Precipitation") # Removed template="plotly_white"
            fig_precip.update_layout(showlegend=False, xaxis_title=None)
            st.plotly_chart(fig_precip, use_container_width=True)

        # --- ROW 2: CURVES ---
        st.subheader("Time-Course Curves")
        
        tab1, tab2, tab3 = st.tabs(["Cell Growth", "Morphology", "Precipitation"])

        with tab1:
            fig_growth_curve = create_curve_plot(
                curve_stats, 
                ('Cell Count', 'mean'), 
                ('Cell Count', 'std'), 
                "Cell Count", 
                "Cell Growth Over Time"
            )
            st.plotly_chart(fig_growth_curve, use_container_width=True)

        with tab2:
            fig_morph_curve = create_curve_plot(
                curve_stats, 
                ('Morphology', 'mean'), 
                ('Morphology', 'std'), 
                "Morphology Score", 
                "Morphology Over Time"
            )
            st.plotly_chart(fig_morph_curve, use_container_width=True)

        with tab3:
            fig_precip_curve = create_curve_plot(
                curve_stats, 
                ('Precipitation', 'mean'), 
                ('Precipitation', 'std'), 
                "Precipitation", 
                "Precipitation Over Time"
            )
            st.plotly_chart(fig_precip_curve, use_container_width=True)

    except Exception as e:
        st.error(f"An error occurred: {e}")
        st.write("Debug Info:", e)
else:
    st.info("Awaiting CSV file upload. Please upload the 'Processed Data' file.")
