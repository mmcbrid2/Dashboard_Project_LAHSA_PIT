import dash
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import geopandas as gpd

# Load and preprocess data for the dashboard

# Define paths to data files
data_path = '2024-housing-inventory-count cleaned.csv'
spa_boundaries_path = 'simplified_SPA.geojson'

# Read in the cleaned housing inventory data
df = pd.read_csv(data_path)

# Load Service Planning Area (SPA) boundaries using GeoPandas for spatial analysis
spa_geo = gpd.read_file(spa_boundaries_path)

# Ensure SPA identifiers are consistent across dataframes
df['SPA'] = df['SPA'].astype(str)
spa_geo['SPA'] = spa_geo['SPA'].astype(str)

# Map SPA numeric identifiers to meaningful names for readability and analysis
spa_dict = {
    '1': 'Antelope Valley',
    '2': 'San Fernando Valley',
    '3': 'San Gabriel Valley',
    '4': 'Metro Los Angeles',
    '5': 'West Los Angeles',
    '6': 'South Los Angeles',
    '7': 'East Los Angeles',
    '8': 'South Bay/Harbor'
}

# Apply SPA name mapping to both datasets
df['SPA'] = df['SPA'].map(spa_dict)
spa_geo['SPA'] = spa_geo['SPA'].map(spa_dict)

# Define a consistent color mapping for visual consistency across charts
color_mapping = {
    'Antelope Valley': '#636EFA',    # Blue
    'San Fernando Valley': '#EF553B',  # Red
    'San Gabriel Valley': '#00CC96',  # Green
    'Metro Los Angeles': '#AB63FA',  # Purple
    'West Los Angeles': '#FFA15A',  # Orange
    'South Los Angeles': '#19D3F3',  # Cyan
    'East Los Angeles': '#FF6692',  # Pink
    'South Bay/Harbor': '#B6E880'   # Light Green
}

# Prepare dropdown options, including a "Select All" option for convenience
dropdown_options = [{'label': 'Select All', 'value': 'ALL'}] + [{'label': spa, 'value': spa} for spa in df['SPA'].unique()]

# Initialize the Dash app with a dark theme for a modern, professional look
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.SLATE])

server = app.server

# Define the layout of the app using Bootstrap components for responsiveness
app.layout = dbc.Container([
    dcc.Loading(  # Provide user feedback with a loading spinner during data updates
        id="loading-icon",
        children=[
            # Title row with main heading and subheading
            dbc.Row([
                dbc.Col([
                    html.H1("2024 Point-In-Time (PIT) Bed Utilization Rate Analysis",
                            className='text-center text-light mb-2'),
                    html.H3("Los Angeles Homeless Services Authority (LAHSA)",
                            className='text-center text-light mb-4')
                ], width=12)
            ]),
            # Dropdown selection for SPAs
            dbc.Row([
                dbc.Col([
                    html.Label("Select Service Planning Area (SPA)", style={'color': 'white'}),
                    dcc.Dropdown(
                        id='slicer-dropdown',
                        options=dropdown_options,
                        multi=True,
                        value=df['SPA'].unique().tolist(),  # Default selection: all SPAs
                        placeholder='Select SPA...',
                        className='mb-3',
                        style={
                            'backgroundColor': 'rgba(169,169,169,1)',  # Set dropdown background color
                            'color': 'black',  # Set dropdown text color
                            'fontWeight': 'bold'  # Bold text for enhanced readability
                        }
                    )
                ], width=12)
            ]),
            # First row of visualizations: Map and Bar chart of Utilization Rate by SPA
            dbc.Row([
                dbc.Col(dcc.Graph(id='map-graph'), width=6),  # Map visualization
                dbc.Col(dcc.Graph(id='bar-graph', config={'displayModeBar': False}), width=6)  # Bar chart
            ]),
            # Second row of visualizations: Utilization by Housing Type and Bed Count
            dbc.Row([
                dbc.Col(dcc.Graph(id='housing-type-bar', config={'displayModeBar': False}), width=6),
                dbc.Col(dcc.Graph(id='bed-count-bar', config={'displayModeBar': False}), width=6)
            ], style={'marginTop': '20px'})  # Margin between rows for better spacing
        ]
    )
], fluid=True)  # Fluid layout for full-width responsiveness

# Define the callback function to update visualizations based on dropdown selection
@app.callback(
    [Output('map-graph', 'figure'),
     Output('bar-graph', 'figure'),
     Output('housing-type-bar', 'figure'),
     Output('bed-count-bar', 'figure'),
     Output('slicer-dropdown', 'value')],  # Return the updated dropdown value as well
    [Input('slicer-dropdown', 'value')]
)
def update_visuals(selected_values):
    # Implement "Select All" functionality by checking if 'ALL' is selected
    if 'ALL' in selected_values:
        selected_values = df['SPA'].unique().tolist()

    # Filter the DataFrame based on the selected SPAs
    filtered_df = df[df['SPA'].isin(selected_values)] if selected_values else df

    # Map visualization: display SPA boundaries and their average utilization rates
    grouped = df.groupby('SPA').agg({'Utilization Rate': 'mean'}).reset_index()
    merged = spa_geo.merge(grouped, left_on='SPA', right_on='SPA', how='left')
    filtered_geo = merged[merged['SPA'].isin(selected_values)] if selected_values else merged

    map_fig = px.choropleth_mapbox(
        filtered_geo,
        geojson=filtered_geo.geometry,
        locations=filtered_geo.index,
        color='SPA',
        hover_name='SPA',
        hover_data={'Utilization Rate': True},
        mapbox_style="carto-positron",  # Use a light map style for better contrast
        center={"lat": 34.0522, "lon": -118.2437},
        zoom=7.35,
        opacity=0.75,
        color_discrete_map=color_mapping  # Apply SPA color mapping
    )
    map_fig.update_layout(showlegend=False,  # Remove legend for clarity
                          margin={"r":5,"t":5,"l":5,"b":5},  # Adjust margins to fit content
                          paper_bgcolor='rgba(169,169,169,1)',  # Match background to theme
                          plot_bgcolor='rgba(169,169,169,1)',
                          modebar_remove=['pan2d', 'select2d', 'lasso2d', 'zoomInGeo', 'zoomOutGeo', 'hoverClosestGeo', 'hoverClosestCartesian', 'hoverCompareCartesian', 'toggleHover', 'toImage'],
                          modebar_add=['zoomIn2d', 'zoomOut2d', 'resetScale2d']  # Customize toolbar options
                         )  

    # Bar chart visualization: display average bed utilization rate by SPA
    bar_fig = px.bar(
        filtered_geo,
        x='SPA',
        y='Utilization Rate',
        color='SPA',
        text='Utilization Rate',  # Display data labels on bars
        title='Average Bed Utilization Rate by SPA',
        labels={'Utilization Rate': 'Avg. Utilization Rate  (%)'},
        color_discrete_map=color_mapping  # Maintain consistent color mapping
    )
    bar_fig.update_traces(texttemplate='%{text:.1f}', textposition='outside')
    bar_fig.update_yaxes(range=[60, 105])  # Set y-axis range to ensure clarity
    bar_fig.update_layout(showlegend=False,  # Remove legend as it is redundant
                          paper_bgcolor='rgba(169,169,169,1)',  # Maintain theme consistency
                          plot_bgcolor='rgba(169,169,169,1)'
                         )

    # Utilization Rate by Housing Type Bar Graph
    # Define color sequence for housing types to ensure differentiation from SPAs
    color_sequence = ['#4D4D4D', '#FFFF66', '#FFFFFF']  

    # Group data by SPA and Housing Type, then calculate mean utilization rates
    housing_grouped = filtered_df.groupby(['SPA', 'Housing Type']).agg({'Utilization Rate': 'mean'}).reset_index()

    housing_type_bar_fig = px.bar(
        housing_grouped,
        x='SPA',
        y='Utilization Rate',
        color='Housing Type',
        barmode='group',
        title='Average Bed Utilization Rate by Housing Type by SPA',
        labels={'Utilization Rate': 'Avg. Utilization Rate  (%)'},
        color_discrete_sequence=color_sequence  # Apply differentiated color palette
    )
    
    # Update layout to add gridlines for improved readability
    housing_type_bar_fig.update_layout(
        yaxis=dict(
            tickmode='linear',
            tick0=0,
            dtick=10,  # Major gridlines every 10 units
            gridwidth=2,
            gridcolor='white',
            showgrid=True,
            minor=dict(
                tickmode='linear',
                tick0=0,
                dtick=5,  # Minor gridlines every 5 units (unlabeled)
                showgrid=True,
                gridwidth=0.5,  # Minor gridline width
                gridcolor='gray'  # Minor gridline color
            )
        ),
        paper_bgcolor='rgba(169,169,169,1)',  # Maintain theme consistency
        plot_bgcolor='rgba(169,169,169,1)',
        legend_title_text='Housing Type'  # Update legend title for clarity
    )

    # Bed Count Bar Graph (Utilized vs Empty Beds)
    # Group data by SPA and calculate sum of utilized and empty beds
    bed_grouped = filtered_df.groupby('SPA').agg({'PIT Count': 'sum', 'Total Beds': 'sum'}).reset_index()
    bed_grouped['Empty Beds'] = bed_grouped['Total Beds'] - bed_grouped['PIT Count']

    # Rename columns for clarity and consistency
    bed_grouped = bed_grouped.rename(columns={"PIT Count": "Utilized Beds"})

    # Transform data for easy plotting in a grouped bar chart
    bed_melted = bed_grouped.melt(id_vars='SPA', value_vars=['Utilized Beds', 'Empty Beds'], var_name='Bed Status', value_name='Bed Count')

    # Create bar graph for bed count comparison between utilized and empty beds
    bed_count_bar_fig = px.bar(
        bed_melted,
        x='SPA',
        y='Bed Count',
        color='Bed Status',
        barmode='group',
        title='Count of Bed Utilization by SPA',
        color_discrete_sequence=color_sequence[:2]  # Apply consistent color scheme
    )

    # Update layout to make the y-axis dynamic for better scaling
    bed_count_bar_fig.update_layout(
        yaxis=dict(
            automargin=True,  # Automatically adjust margins for better presentation
            title='Bed Count',
            title_standoff=10,  # Adds space between the title and axis labels
            gridcolor='white',  # Set major gridline color to white for visibility
            zeroline=True,  # Include a zero line for reference
            zerolinewidth=2,
            zerolinecolor='gray',
        ),
        paper_bgcolor='rgba(169,169,169,1)',  # Maintain background color consistency
        plot_bgcolor='rgba(169,169,169,1)',
        legend_title_text=''  # Remove the 'Bed Status' label for a cleaner look
    )

    return map_fig, bar_fig, housing_type_bar_fig, bed_count_bar_fig, selected_values  # Return updated dropdown value

# Run the server after configuration is complete
if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 8050))  # Get the port from environment variable or default to 8050
    app.run_server(debug=True, host='0.0.0.0', port=port)  # Bind to 0.0.0.0 to be accessible externally












