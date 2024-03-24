import streamlit as st
import plotly.express as px
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# Import the necessary CSVs to Pandas DataFrames
file_path = Path("Data/sfo_neighborhoods_census_data.csv")
sfo_data = pd.read_csv(file_path, index_col="year")

# Define Visualization Functions
def housing_units_per_year():
    """Housing Units Per Year.""" 
    year_grouped_df = sfo_data['housing_units'].groupby(sfo_data.index).mean()
    units_fig = px.bar(year_grouped_df, y=["housing_units"], range_y=[370000, 385000])
    return units_fig


def average_gross_rent():
    """Average Gross Rent in San Francisco Per Year."""
    # Line chart for average montly rent
    average_rent_df = sfo_data['gross_rent'].groupby(sfo_data.index).mean()
    rent_fig = px.line(average_rent_df, x=average_rent_df.index, y=["gross_rent"], labels={"x": "Year", "value": "Average Rent"})
    rent_fig.update_layout(showlegend=False)
    return rent_fig


def average_sales_price():
    """Average Sales Price Per Year."""
    average_ppsf_df = sfo_data['sale_price_sqr_foot'].groupby(sfo_data.index).mean()
    # Line chart for average sale price per square foot
    sqft_fig = px.line(average_ppsf_df, x=average_ppsf_df.index, y=["sale_price_sqr_foot"], labels={"x": "Year", "value": "Average Price (USD) per Square Foot"})
    sqft_fig.update_layout(showlegend=False)
    return sqft_fig


def average_price_by_neighborhood(neighborhood):
    df_prices = sfo_data.loc[sfo_data["neighborhood"] == neighborhood]
    df_prices["sale_price_sqr_foot"] = pd.to_numeric(df_prices["sale_price_sqr_foot"], errors="coerce")
    df_prices.dropna(inplace=True)
    df_prices_grouped = df_prices["sale_price_sqr_foot"].groupby(df_prices.index).mean()
    sqft_fig = px.line(df_prices_grouped, x=df_prices_grouped.index, y=["sale_price_sqr_foot"], labels={"x": "Year", "value": "Average Price (USD) per Square Foot"})
    sqft_fig.update_layout(showlegend=False)
    return sqft_fig


def average_rent_by_neighborhood(neighborhood):
    df_rent = sfo_data.loc[sfo_data["neighborhood"] == neighborhood]
    df_rent["gross_rent"] = pd.to_numeric(df_rent["gross_rent"], errors="coerce")
    df_rent.dropna(inplace=True)
    df_rent_grouped = df_rent["gross_rent"].groupby(df_rent.index).mean()
    sqft_fig = px.line(df_rent_grouped, x=df_rent_grouped.index, y=["gross_rent"], labels={"x": "Year", "value": "Average Rent (USD)"})
    sqft_fig.update_layout(showlegend=False)
    return sqft_fig


def top_most_expensive_neighborhoods():
    """Top 10 Most Expensive Neighborhoods."""
    top_cost_df = sfo_data[["neighborhood", "sale_price_sqr_foot"]].groupby(["neighborhood"]).mean().round(2)
    top_cost_df.sort_values(by="sale_price_sqr_foot", ascending=False, inplace=True)
    top_ten_df = top_cost_df.head(10)
    # Plotting the data from the top 10 expensive neighborhoods
    top_cost_fig = px.bar(top_ten_df, labels={"neighborhood": "Most Expensive Neighborhoods", "value": "Average Price per Square Foot (USD)"})
    top_cost_fig.update_layout(showlegend=False)
    # Show the plot
    return top_cost_fig

def most_expensive_neighborhoods_rent_sales(neighborhood):
    # Filter sfo_data based on selected_neighborhood
    df_costs = sfo_data[sfo_data["neighborhood"] == neighborhood]
    df_costs.rename(columns={"sale_price_sqr_foot": "Sale price square foot", "gross_rent": "Rent"}, inplace=True)

    # Generate Plotly bar chart for Price per sq foot and rent
    fig = px.bar(df_costs, x=df_costs.index, y=["Sale price square foot", "Rent"],
                 title=f"{neighborhood} Neighborhood Comparison",
                 labels={"index": "Year", "value": "Price in USD"},
                 barmode="group")

    return fig
    
    
def neighborhood_map():
    """Neighborhood Map."""

    file_path = Path("Data/neighborhoods_coordinates.csv")
    sfo_coord_data = pd.read_csv(file_path, index_col="Neighborhood")
    # Create mean_rent_df by grouping sfo_data by neighborhood and calculating the mean of gross_rent
    mean_rent_df = sfo_data.groupby("neighborhood")["gross_rent"].mean().round(2).reset_index()
    mean_rent_df.rename(columns={"gross_rent": "Average Rent"}, inplace=True)

    # Join the average values with the neighborhood locations
    sfo_coord_rents_df = pd.merge(sfo_coord_data, mean_rent_df, left_on="Neighborhood", right_on="neighborhood")

    # Rename neighborhood to Neighborhood column after the merge
    sfo_coord_rents_df.rename(columns={"neighborhood":"Neighborhood"}, inplace=True)
    sfo_coord_rents_df.set_index('Neighborhood', inplace=True)
    
    # Create a scatter mapbox to analyze neighborhood info
    fig = px.scatter_mapbox(
        sfo_coord_rents_df,
        lat='Lat',
        lon='Lon',
        hover_name=sfo_coord_rents_df.index,  # Use Neighborhood as hover name
        hover_data={'Lat': False, 'Lon': False},  # Hide Lat and Lon from hover data
        color='Average Rent',  # Color points based on Average Rent
        size='Average Rent',  # Size points based on Average Rent
        color_continuous_scale='thermal',  # Color scale
        size_max=15,  # Maximum point size
        zoom=10,  # Set initial zoom level
        mapbox_style='carto-positron'  # Map style
    )

    # Update layout
    fig.update_layout(
        title='Average Rent per Neighborhood',
        mapbox=dict(
            center=dict(lat=sfo_coord_rents_df['Lat'].mean(), lon=sfo_coord_rents_df['Lon'].mean()),  # Set map center
        )
    )

    # Show the plot
    return fig


# Start Streamlit App

st.header("San Francisco Real Estate Analysis")
# Import image
image_path = "img/sf_homeless.jpg"
st.image(image_path, caption='Lovely SF', use_column_width=True)
st.write(f"Come to San Francisco where you can dodge fentynal zombies while paying some of the highest housing costs in the nation! Check out these charts to help you select the perfect home for your family.")


tab1, tab2, tab3, tab4 = st.tabs(["Yearly averages", "Neighborhoods", "Most Expensive", "Mapped"])

with tab1:
    st.header("Yearly averages")

    with st.expander("Housing Units Per Year", expanded=True):
        st.subheader(f"Housing Units Per Year")
        st.plotly_chart(housing_units_per_year())

    with st.expander("Average Gross Rent per Year"):
        st.subheader(f"Average Gross Rent per Year")
        st.plotly_chart(average_gross_rent())
    
    with st.expander("Average Sales Price per Year"):
        st.subheader(f"Average Sales Price per Year")
        st.plotly_chart(average_sales_price())

with tab2:
    neighborhood = "Alamo Square"
    st.header("Neighborhoods")
    neighborhood = st.selectbox(
        "Select a Neighborhood:",
        ['Alamo Square', 'Anza Vista', 'Bayview', 'Bayview Heights',
       'Buena Vista Park', 'Central Richmond', 'Central Sunset',
       'Clarendon Heights', 'Corona Heights', 'Cow Hollow', 'Croker Amazon',
       'Diamond Heights', 'Duboce Triangle', 'Eureka Valley/Dolores Heights',
       'Excelsior', 'Financial District North', 'Financial District South',
       'Forest Knolls', 'Glen Park', 'Golden Gate Heights', 'Haight Ashbury',
       'Hayes Valley', 'Hunters Point', 'Ingleside Heights', 'Inner Mission',
       'Inner Parkside', 'Inner Richmond', 'Inner Sunset',
       'Jordan Park/Laurel Heights', 'Lake --The Presidio', 'Lone Mountain',
       'Lower Pacific Heights', 'Marina', 'Merced Heights', 'Midtown Terrace',
       'Miraloma Park', 'Mission Bay', 'Mission Dolores', 'Mission Terrace',
       'Nob Hill', 'Noe Valley', 'North Beach', 'North Waterfront',
       'Oceanview', 'Outer Mission', 'Outer Parkside', 'Outer Sunset',
       'Pacific Heights', 'Park North', 'Parkside',
       'Parnassus/Ashbury Heights', 'Portola', 'Potrero Hill',
       'Presidio Heights', 'Russian Hill', 'Silver Terrace', 'South Beach',
       'South of Market', 'Sunnyside', 'Telegraph Hill', 'Twin Peaks',
       'Union Square District', 'Van Ness/ Civic Center', 'Visitacion Valley',
       'West Portal', 'Western Addition', 'Westwood Highlands',
       'Westwood Park', 'Yerba Buena']
    )

    st.subheader(f"Average Yearly Sales Price for {neighborhood}")
    st.plotly_chart(average_price_by_neighborhood(neighborhood))

    st.subheader(f"Average Yearly Rent for {neighborhood}")
    st.plotly_chart(average_rent_by_neighborhood(neighborhood))

    st.subheader(f"Price per Square Foot vs Rent for {neighborhood}")
    st.plotly_chart(most_expensive_neighborhoods_rent_sales(neighborhood))

with tab3:
    st.header("Most Expensive")
    
    st.subheader(f"Top Ten Neighborhoods(Price per Square Foot)")
    st.plotly_chart(top_most_expensive_neighborhoods())

with tab4:
    st.header("Mapped")
    st.plotly_chart(neighborhood_map())
