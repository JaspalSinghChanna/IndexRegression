from analytics_module import Analytics
import dash
from dash import dcc, html, Input, Output, callback, dash_table
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
import plotly.express as px
import datetime
import pandas as pd
import numpy as np
import logging

a = Analytics()

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.SOLAR])

app.layout = dbc.Container([
    dbc.Row(html.H1("Multi-Variate Index Regression"), className='text-center'),
    dbc.Row(html.H6("This tool allows a user to see how much of the variance (daily returns) of a selected index can be explained by a basket of securities. Daily returns are calculated using end-of-day close prices.")),
    dbc.Row([
        dbc.Col([
            html.Div("Select an index:", className="mb-2"),
            dcc.Dropdown(
                options=[
                    {'label': 'S&P 500', 'value': '^GSPC'},
                    {'label': 'Nasdaq 100', 'value': '^NDX'},
                    {'label': 'Russell 2000', 'value': '^RUT'},
                ],
                value="^GSPC",
                id='index-dropdown',
                
            ),
            html.Div(id='index-dropdown-output-container')
        ]),
        dbc.Col([
            html.Div("Select tickers:", className="mb-2"),
            dcc.Dropdown(
                options=a.tl,
                value=['MSFT', 'AAPL'],
                id='security-dropdown',
                multi=True,
                placeholder='Select securities'
            ),
            html.Div(id='security-dropdown-output-container')
        ])
    ]),
    dbc.Row([
        dbc.Col([
            html.Div("Select a date range (optional):", className="mb-2"),
            dcc.DatePickerRange(
                id='date-range',
                min_date_allowed=datetime.date(1960, 1, 1),
                max_date_allowed=datetime.date(2024, 1, 1),
                clearable=True
            ),
        ]),
        dbc.Col([
            html.Div("Select aggregation level (optional):", className="mb-2"),
            dcc.Dropdown(
                options=[
                    {'label': 'Daily', 'value': 'Daily'},
                    {'label': 'Monthly Average', 'value': 'M'},
                    {'label': 'Quarterly Average', 'value': 'Q'},
                    {'label': 'Annual Average', 'value': 'Y'},
                ],
                value='Daily',
                id='agg-dropdown'
            ),
        ]),
    ]),
    dbc.Row([
        dbc.Col(
            dcc.Graph(figure={}, id='scatter-graph'),
        )
    ], className="p-4"),
    dbc.Row([
        dbc.Col(
            dbc.Label('Weightings From Regression')),
        dbc.Col(
            dbc.Label('R-squared'))
    ]),
    dbc.Row([
        dbc.Col(
            dash_table.DataTable(id='df_datatable', page_size=11,
            style_header={'backgroundColor': 'rgb(30, 30, 30)','color': 'white'},
            style_data={'backgroundColor': 'rgb(50, 50, 50)','color': 'white'},)),
        dbc.Col([
            dbc.Card(id='r2-card',style={"font-size": "20px",
                                        "text-align": "center"}),
            dbc.Label('Sum of weightings of all selected securities', className='mt-2'),
            dbc.Card(id='weightings-card',style={"font-size": "20px",
                                        "text-align": "center"}),
        ])
    ])
], className="p-4")


@callback(
    [Output(component_id='scatter-graph', component_property='figure'),
    Output(component_id='df_datatable', component_property='data'),
    Output(component_id='r2-card', component_property='children'),
    Output(component_id='weightings-card', component_property='children')],
    [
        Input(component_id='security-dropdown', component_property='value'),
        Input(component_id='index-dropdown', component_property='value'),
        Input(component_id='date-range', component_property='start_date'),
        Input(component_id='date-range', component_property='end_date'),
        Input(component_id='agg-dropdown', component_property='value')
    ]
)
def update_graph(sec_value, index_value, start_date, end_date, agg_value):
    logging.info(sec_value)
    logging.info(index_value)
    
    if index_value is None:
        raise PreventUpdate
    elif sec_value == []:
        raise PreventUpdate
    else:
        ticker_records = a.get_ticker_records(sec_value + [index_value])
        prepped_data = a.prep_data(ticker_records)
        df, reg, r2, weightings = a.get_contributions(prepped_data, index_value)
        weightings_sum = round(weightings['Weightings'].sum(), 5)
        if agg_value:
            if agg_value!='Daily':
                df = df.groupby([pd.Grouper(freq=agg_value)]).agg(np.mean)
        df = df.mul(100)
        df = df.reset_index()
        if start_date:
            st_dt = datetime.datetime.strptime(start_date, '%Y-%m-%d') 
            df = df.loc[df['Date'] >= st_dt]
        if end_date:
            ed_dt = datetime.datetime.strptime(end_date, '%Y-%m-%d')
            df = df.loc[df['Date'] <= ed_dt]
        sc1 = px.scatter(x=df['Date'],y=df['Predictions'],
                         title="Returns Over Time", 
                         labels={'x': 'Time', 'y':'(Average) Daily Return (%)'})
        sc1['data'][0]['showlegend']=True
        sc1['data'][0]['name']='Basket of Securities'
        sc1.add_scatter(x=df['Date'],y=df[index_value], name='Index')

        return [sc1, weightings.round(5).to_dict("records"), round(r2, 5), weightings_sum]
    

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True, port=8053)