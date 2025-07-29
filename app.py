import streamlit as st
import pandas as pd
import os

# --- Page Configuration ---
st.set_page_config(
    page_title="SLOSH Inundation Zone Economic Impacts",
    layout="wide"
)

# --- Data Loading ---
# Use st.cache_data to load data only once
@st.cache_data
def load_data(file_path):
    """Loads the CSV data into a pandas DataFrame."""
    try:
        return pd.read_csv(file_path)
    except FileNotFoundError:
        st.error(f"Error: The file '{file_path}' was not found. Please make sure it's in the correct directory.")
        return None

# --- Main Application ---
def main():
    """Main function to run the Streamlit app."""
    st.title("Economic Impacts of SLOSH Inundation Zones")
    st.markdown("Select a state, county, and storm category to see the potential economic impacts on local businesses.")

    # Load data
    df = load_data("Expected losses by SLOSH inundation zone.csv")

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
                inundation_types = sorted(df[(df['State'] == selected_state) & (df['County'] == selected_county)]['SLOSH'].unique())
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
                (df['SLOSH'] == selected_inundation)
            ].iloc[0]

            # Extract data from the selected row
            establishments = int(selection_data['Establishments'])
            employment = int(selection_data['Employment'])
            wages_week = selection_data['wages_week']
            sales_week = selection_data['sales_week']

            # Format monetary values to millions, rounded to the nearest 100,000
            lost_wages_millions = round(wages_week / 1_000_000, 1)
            lost_sales_millions = round(sales_week / 1_000_000, 1)

            # --- Display Title and Map ---
            st.header(f"Employment in {selected_county} County, {selected_state} inundation zones for a {selected_inundation.lower()}")

            # A mapping of full state names to their abbreviations for file naming
            state_abbreviations = {
                'Alabama': 'AL',
                'Mississippi': 'MS',
                # Add other states and abbreviations as needed
            }

            # Construct the image file path
            state_abbr = state_abbreviations.get(selected_state, '')
            slosh_cat_num = ''.join(filter(str.isdigit, selected_inundation))
            image_name = f"{selected_county}_{state_abbr}_cat{slosh_cat_num}.jpg"
            image_path = os.path.join("Inundation Maps", image_name)

            if os.path.exists(image_path):
                st.image(image_path, caption=f"Inundation zone map for {selected_county} County, {selected_state} - {selected_inundation}")
            else:
                st.warning(f"Map file not found at the expected path: {image_path}. Please ensure maps are in the 'Inundation Maps' folder.")

            # --- Display Key Statistics ---
            st.subheader("Key Business Statistics")
            st.markdown(f"""
            - In 2021, there were approximately **{establishments:,}** {selected_county} County employers in a {selected_inundation.lower()} inundation zone.
            - **{employment:,}** people worked at those businesses.
            - A one-week closure of establishments in this inundation zone would result in about **${lost_wages_millions:.1f} million** in lost wages and about **${lost_sales_millions:.1f} million** in lost business sales.
            """)
        else:
            st.info("Please complete all selections above to view the analysis.")

if __name__ == "__main__":
    main()
