""" This file is used to create the layout for the main.py file """

from dash import Dash, html, dcc
import dash_bootstrap_components as dbc
from src.components.dropdowns import ave_tab_months_dropdown, ave_tab_options_dropdown
from src.components.charts_and_tables import main_chart, main_table

from src.components.layout import ids
from src.components.dropdowns import main_tab_dropdowns
from src.components.charts_and_tables import ave_table

def create_layout(app: Dash):
    """ Create layout to be used in main.py file """
    return html.Div(
        children=[
            # App Title
            html.H1(app.title, style={'textAlign': 'center', 'margin-top':'15px', 'color':'blue'}),
            html.Hr(),
            dcc.Tabs([
                # Main Tab
                dcc.Tab(label='Main', children=[
                    html.Div(
                        [
                            dbc.Row(
                                [
                                    # Dropdowns
                                    dbc.Col(
                                        [
                                            html.Div(
                                                className="dropdowns", children=[main_tab_dropdowns.render(app)], style = {'margin-left':'15px', 'margin-top':'15px', 'margin-right':'15px', 'margin-bottom':'15px'}
                                            )
                                        ], width=3
                                    ),
                                    # Chart and table
                                    dbc.Col([
                                        html.Div(children=[main_chart.render(app)], id=ids.CHART),
                                        html.Div(children=[main_table.render(app)], id=ids.TABLE, style={'margin-right':'25px'}),
                                    ], width=9)
                                ], justify="evenly", style = {'margin-left':'15px', 'margin-right':'15px'}
                            )
                        ]
                    )
                ]),
                # Averages Tab
                dcc.Tab(label='Averages', children=[
                    html.Div(
                        className="app-div",
                        children=[
                            html.Hr(),
                            html.Div([dbc.Row(
                            # Dropdowns
                            [
                                dbc.Col([
                                    html.Div(
                                        children=[
                                            html.H6('Choose category: Properties or Offices'),
                                            dcc.Dropdown(['Property', 'Office'], 'Property', id=ids.O_OR_P_AVE, clearable=False, searchable=False)
                                        ], style={'margin-bottom': '15px'}),
                                    html.Div(className="dropdown_container", children=[ave_tab_options_dropdown.render(app)])
                                    ], width=6
                                ),
                                dbc.Col(html.Div(className="dates_dropdown_container", children=[ave_tab_months_dropdown.render(app)]), width=6),
                            ], justify="evenly", style = {'margin-left':'15px', 'margin-top':'15px', 'margin-right':'15px'}),]),
                            # Tables
                            html.Div([ave_table.render(app)], id=ids.AVE),
                            html.Hr(),
                        ],
                    )
                ])
            ])
        ])