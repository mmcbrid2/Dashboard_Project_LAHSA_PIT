2024 Point-In-Time (PIT) Bed Utilization Rate Analysis Dashboard

Overview

This project presents an interactive dashboard built using Dash and Plotly to analyze and visualize the 2024 Point-In-Time (PIT) Bed Utilization Rate for the Los Angeles Homeless Services Authority (LAHSA). The dashboard provides stakeholders with insights into bed utilization across various Service Planning Areas (SPAs) in Los Angeles, offering visualizations of average utilization rates by SPA, housing type, and bed status (utilized vs. empty beds).

Table of Contents

Project Structure
Installation
Usage
Features
Data Sources
Contributing
Project Structure

├── README.md
├── LAHSA_Dash.py # Main dashboard script
├── 2024-housing-inventory-count cleaned.csv # Data file from LASHA housing website inventory
├── Service_Planning_Areas_2022_view_4712258077157513619.geojson # GeoJSON file for SPA boundaries from LA County
└── requirements.txt # Python package requirements

Usage

Once the dashboard is running, you can interact with various visualizations:

Service Planning Area (SPA) Selection: Use the dropdown to select specific SPAs or click "Select All" to view data for all SPAs.
Map Visualization: Shows the geographic distribution of bed utilization rates across selected SPAs.
Bar Graphs: Visualize average bed utilization by SPA, housing type, and bed status (utilized vs. empty beds).
These features enable stakeholders to gain insights into the bed utilization patterns across Los Angeles, helping them make data-driven decisions.

Features

Dynamic SPA Selection: Select one or multiple SPAs from the dropdown to update the visualizations dynamically.
Interactive Map: A choropleth map that visually represents the bed utilization rate across different SPAs.
Responsive Layout: The dashboard is fully responsive, ensuring a seamless experience across various screen sizes.
Gridlines & Legends: Customizable gridlines and legends for better data interpretation and visualization.
