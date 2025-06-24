# Import required libraries
import pandas as pd
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("../data/processed/spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Get unique launch sites for dropdown options
launch_sites = spacex_df['Launch Site'].unique()

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                 dcc.Dropdown(id='site-dropdown',
                                                options=[{'label': 'All Sites', 'value': 'ALL'}] + 
                                                        [{'label': site, 'value': site} for site in launch_sites],
                                                value='ALL',
                                                placeholder="Select a launch site here",
                                                searchable=True
                                                 ),
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                
                                # TASK 3: Add a slider to select payload range
                                dcc.RangeSlider(id='payload-slider',
                                                min=0, max=10000, step=1000,
                                                marks={i: str(i) for i in range(0, 11000, 1000)},
                                                value=[min_payload, max_payload]),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
@app.callback(Output(component_id='success-pie-chart', component_property='figure'),
              Input(component_id='site-dropdown', component_property='value'))
def get_pie_chart(entered_site):
    if entered_site == 'ALL':
        # Show total successful launches count for all sites
        success_counts = spacex_df.groupby('Launch Site')['class'].sum().reset_index()
        fig = px.pie(success_counts, 
                     values='class', 
                     names='Launch Site', 
                     title='Total Success Launches by Site')
        return fig
    else:
        # Show Success vs Failed counts for the selected site
        filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site]
        success_failure_counts = filtered_df['class'].value_counts().reset_index()
        success_failure_counts.columns = ['class', 'count']
        
        fig = px.pie(success_failure_counts,
                     values='count',
                     names='class',
                     title=f'Total Success vs Failure for {entered_site}',
                     color='class',
                     color_discrete_map={0: '#ff7f7f', 1: '#90ee90'})
        
        # Update labels to be more descriptive
        fig.update_traces(labels=['Failure', 'Success'])
        return fig

# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(Output(component_id='success-payload-scatter-chart', component_property='figure'),
              [Input(component_id='site-dropdown', component_property='value'),
               Input(component_id="payload-slider", component_property="value")])
def update_scatter_chart(selected_site, payload_range):
    # Filter by payload range
    filtered_df = spacex_df[
        (spacex_df['Payload Mass (kg)'] >= payload_range[0]) & 
        (spacex_df['Payload Mass (kg)'] <= payload_range[1])
    ]
    
    # Filter by site if necessary
    if selected_site != 'ALL':
        filtered_df = filtered_df[filtered_df['Launch Site'] == selected_site]
    
    # Create scatter plot
    fig = px.scatter(
        filtered_df,
        x='Payload Mass (kg)',
        y='class',
        color='Booster Version Category',
        title='Correlation between Payload and Launch Success',
        labels={'class': 'Launch Outcome (0=Failure, 1=Success)'},
        hover_data=['Launch Site', 'Booster Version']
    )
    
    # Customize the plot
    fig.update_layout(
        yaxis=dict(
            tickmode='array',
            tickvals=[0, 1],
            ticktext=['Failure', 'Success']
        ),
        hovermode='closest'
    )
    
    return fig

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True, use_reloader=False)  # Turn off reloader if inside Jupyter environment