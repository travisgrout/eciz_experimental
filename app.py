import streamlit as st
import pandas as pd
import os

# --- Page Configuration ---
st.set_page_config(
    page_title="Employment in Coastal Inundation Zones",
    layout="wide"
)

# --- Data Loading ---
# Use st.cache_data to load data only once
@st.cache_data
def load_data(file_path):
    """Loads the CSV data into a pandas DataFrame."""
    try:
        # Load the new CSV file
        return pd.read_csv(file_path)
    except FileNotFoundError:
        st.error(f"Error: The file '{file_path}' was not found. Please make sure it's in the correct directory.")
        return None

@st.dialog("Inundation Map")
def view_map_dialog(image_path):
    """Displays the map image in a dialog."""
    if os.path.exists(image_path):
        # Removed use_container_width to display the image at its actual size
        st.image(image_path) 
    else:
        st.error("Map image could not be found.")

# --- Main Application ---
def main():
    """Main function to run the Streamlit app."""

    st.title("Employment in Coastal Inundation Zones")
    st.markdown("Select a state, county, and storm category to learn about the potential economic impacts on local businesses.")

    # Load data from the new spreadsheet
    df = load_data("Expected losses by county and zone.csv")

    if df is not None:
        # --- User Selections ---
        col1, col2, col3 = st.columns(3)

        with col1:
            # State selection
            states = sorted(df['State'].unique())
            selected_state = st.selectbox("Select a State", [""] + states)

        with col2:
            # County selection (populated based on state)
            if selected_state:
                counties = sorted(df[df['State'] == selected_state]['County'].unique())
                selected_county = st.selectbox("Select a County", [""] + counties)
            else:
                st.selectbox("Select a County", [], disabled=True)
                selected_county = None

        with col3:
            # Inundation type selection (populated based on state and county)
            if selected_state and selected_county:
                # The 'inundation_zone' column holds the user-friendly name
                inundation_types = sorted(df[(df['State'] == selected_state) & (df['County'] == selected_county)]['inundation_zone'].unique())
                selected_inundation = st.selectbox("Select Inundation Type", [""] + inundation_types)
            else:
                st.selectbox("Select Inundation Type", [], disabled=True)
                selected_inundation = None

        st.divider()

        # --- Display Results ---
        if selected_state and selected_county and selected_inundation:
            # Filter DataFrame to get the specific data for the user's selection
            selection_data = df[
                (df['State'] == selected_state) &
                (df['County'] == selected_county) &
                (df['inundation_zone'] == selected_inundation)
            ].iloc[0]

            # --- Extract Data ---
            establishments = int(selection_data['Establishments'])
            employment = int(selection_data['Employment'])
            wages_week = selection_data['wages_week']
            sales_week = selection_data['sales_week']
            county_establishments = int(selection_data['county_establishments'])
            county_employment = int(selection_data['county_employment'])
            total_emp_in_zone = int(selection_data['baEMP'])

            # --- Calculations ---
            percent_establishments = round((establishments / county_establishments) * 100) if county_establishments > 0 else 0
            percent_employment = round((employment / county_employment) * 100) if county_employment > 0 else 0
            lost_wages_millions = round(wages_week / 1_000_000, 1)
            lost_sales_millions = round(sales_week / 1_000_000, 1)

            # --- Display Title ---
            # Remove " County" from display title for better readability
            display_county = selected_county.replace(" County", "")
            st.header(f"Employment in {display_county} County, {selected_state} inundation zones: {selected_inundation.lower()}")
            
            # --- Create columns for stats and map ---
            stat_col, map_col = st.columns([3, 2]) # 60/40 split

            with stat_col:
                stats_html = f"""
                <div style='font-size: 18px;'>
                    <ul>
                        <li>In 2021, there were approximately <b>{establishments:,}</b> {display_county} County employers in a {selected_inundation.lower()} inundation zone.<br><i>(<b>{percent_establishments}%</b> of all employers in {display_county} County)</i></li>
                        <li><b>{employment:,}</b> people worked at those businesses.<br><i>(<b>{percent_employment}%</b> of all jobs in {display_county} County)</i></li>
                        <li>A one-week closure of establishments in this inundation zone would result in about <b>${lost_wages_millions:.1f} million</b> in lost wages and about <b>${lost_sales_millions:.1f} million</b> in lost business sales.</li>
                    </ul>
                </div>
                """
                st.markdown(stats_html, unsafe_allow_html=True)

                # --- Generate HTML for Industry Table (Moved to Left Column) ---
                table_rows_html = ""
                for i in range(1, 6):
                    ind_group = selection_data[f'impacted_indgrp_{i}']
                    if pd.notna(ind_group):
                        naics_code = int(selection_data[f'impacted_naics4_{i}'])
                        emp_in_group = int(selection_data[f'emp_naics4_{i}'])
                        emp_percent = round((emp_in_group / total_emp_in_zone) * 100) if total_emp_in_zone > 0 else 0
                        table_rows_html += f"<tr><td>{i}</td><td>{naics_code}</td><td>{ind_group}</td><td><b>{emp_percent}%</b></td></tr>"

                table_html = f"""
                <style>
                    .styled-table {{
                        border-collapse: collapse;
                        margin: 15px 0;
                        font-size: 0.9em; /* Adjusted for better fit */
                        width: 100%;
                    }}
                    .styled-table thead tr {{
                        background-color: #f2f2f2;
                        color: #333;
                        text-align: left;
                    }}
                    .styled-table th,
                    .styled-table td {{
                        padding: 12px 15px;
                        border: 1px solid #ddd;
                    }}
                    .styled-table td:nth-child(1), .styled-table td:nth-child(2), .styled-table td:nth-child(4) {{
                        text-align: center;
                    }}
                </style>
                <p style='font-size: 18px;'>The industry groups most affected by inundation in this zone would be:</p>
                <table class="styled-table">
                    <thead>
                        <tr>
                            <th> </th>
                            <th>NAICS Code</th>
                            <th>Industry Group</th>
                            <th>% of Employment in the Inundation Zone</th>
                        </tr>
                    </thead>
                    <tbody>
                        {table_rows_html}
                    </tbody>
                </table>
                """
                st.markdown(table_html, unsafe_allow_html=True)
            
            # Define image path once to use in the column and the dialog
            state_abbreviations = {'Alabama': 'AL', 'Mississippi': 'MS'}
            state_abbr = state_abbreviations.get(selected_state, '')
            slosh_cat_num = ''.join(filter(str.isdigit, selected_inundation))
            image_name = f"{display_county}_{state_abbr}_cat{slosh_cat_num}.jpg"
            image_path = os.path.join("Inundation Maps", image_name)

            with map_col:
                # --- Display Map ---
                if os.path.exists(image_path):
                    st.image(image_path, caption=f"Inundation zone map for {display_county} County, {selected_state} - {selected_inundation}")
                    
                    # This button now calls the decorated dialog function directly
                    if st.button("View Larger Map"):
                        view_map_dialog(image_path)
                else:
                    st.warning(f"Map file not found at the expected path: {image_path}. Please ensure maps are in the 'Inundation Maps' folder.")
            
        else:
            st.info("Please complete all selections above to view the analysis.")

if __name__ == "__main__":
    main()
