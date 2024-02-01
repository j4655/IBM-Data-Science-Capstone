# Import required libraries
import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()
# print(min_payload)
# print(max_payload)
# print(sorted(spacex_df['Launch Site'].unique()))
sites = sorted(spacex_df['Launch Site'].unique())
site_dropdown_options = [{'label': 'All Sites', 'value': 'ALL'}]
for x in sites:
    site_dropdown_options.append({'label': x, 'value': x})

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                # dcc.Dropdown(id='site-dropdown',...)
                                dcc.Dropdown(
                                    id='site-dropdown', 
                                    options=site_dropdown_options, 
                                    placeholder='Pick a site', 
                                    value='ALL',
                                    searchable=True),
                                html.Br(),


                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                #dcc.RangeSlider(id='payload-slider',...)
                                dcc.RangeSlider(
                                    id='payload-slider',
                                    min=0,
                                    max=10000,
                                    step=1000,
                                    value=[min_payload, max_payload]
                                ),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
# Function decorator to specify function input and output
@app.callback(Output(component_id='success-pie-chart', component_property='figure'),
              Input(component_id='site-dropdown', component_property='value'))
def get_pie_chart(entered_site):
    all_df = spacex_df[['Launch Site', 'class']].groupby('Launch Site').sum().reset_index().sort_values(by='Launch Site')
    # print(all_df)
    if entered_site == 'ALL':
        fig = px.pie(
            all_df, 
            values='class', 
            names='Launch Site', 
            title='title')
        return fig
    else:
        # return the outcomes piechart for a selected site
        filtered_df = spacex_df[spacex_df['Launch Site']==entered_site].reset_index()
        filtered_df['Success/Failure'] = ''
        def tag_success(row):
            if row['class'] == 1:
                row['Success/Failure'] = 'Success'
            else:
                row['Success/Failure'] = 'Failure'
            return row
        filtered_df = filtered_df.apply(tag_success, axis=1).value_counts().reset_index()
        # print(filtered_df[['Success/Failure']].value_counts().reset_index())
        fig = px.pie(
            filtered_df, 
            values='count',
            names='Success/Failure',
            title='title',
            color='Success/Failure',
            color_discrete_map={'Success':'green', 'Failure': 'red'})
        return fig

# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(Output(component_id='success-payload-scatter-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value'),
    Input(component_id='payload-slider', component_property='value'))
def get_scatter_chart(entered_site, payload_range):
    print(f'entered site:\t{entered_site}')
    print(f'payload range {payload_range}')
    filtered_df = spacex_df[
        (spacex_df['Payload Mass (kg)'] >= payload_range[0]) & 
        (spacex_df['Payload Mass (kg)'] <= payload_range[1])
        ].reset_index()
    if entered_site != 'ALL':
        print('hello world')
        filtered_df = filtered_df[filtered_df['Launch Site'] == entered_site].reset_index()
    print(filtered_df.head())
    print(spacex_df.head())
    print(payload_range[1])
    fig = px.scatter(
            filtered_df,
            x='Payload Mass (kg)',
            y='class',
            color='Booster Version Category'
        )
    return fig

# Run the app
if __name__ == '__main__':
    app.run_server()
