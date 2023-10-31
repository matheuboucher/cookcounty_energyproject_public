""" This file renders the dropdowns that allows the user to choose whether they
    wish to see electricity or gas data and usage or spending data, whether to
    group by offices or properties, and which of these offices or properties to
    include. """

from dash import Dash, html, dcc
from dash.dependencies import Input, Output
import src.components.layout.ids as ids
from src.functions import properties, offices

def render(app: Dash):

    @app.callback(
        Output(ids.OFFS_PROPS_DROPDOWN, "value"),
        Output(ids.OFFS_PROPS_DROPDOWN, "options"),
        Input(ids.SELECT_ALL, "n_clicks"),
        Input(ids.OFFICES_OR_PROPS, "value")
    )
    
    # Create a button to select all options of the dropdown
    def select_all_offices(_: int, offsOrProps):
        value = properties if offsOrProps=="Property" else offices
        options = [{'label': val, 'value': val} for val in value]
        return value, options

    return html.Div(
        children=[
            html.Div(
                children=[
                    html.H6('Choose category: Gas or Electricity'),
                    dcc.Dropdown(['Gas', 'Electricity'], 'Gas', id=ids.GAS_OR_ELEC, clearable=False, searchable=False)
                ], style = {'margin-left':'15px', 'margin-top': '45px', 'margin-right':'15px'}
            ),
            html.Div(
                children=[
                    html.H6('Choose category: Usage or Spending'),
                    dcc.Dropdown(['Usage', 'Spending'], 'Usage', id=ids.USAGE_OR_SPENDING, clearable=False, searchable=False)
                ], style = {'margin-left':'15px', 'margin-top':'15px', 'margin-right':'15px'}
            ),
            html.Div(
                children=[
                    html.H6('Choose category: Properties or Offices'),
                    dcc.Dropdown(['Property', 'Office'], 'Property', id=ids.OFFICES_OR_PROPS, clearable=False, searchable=False)
                ], style = {'margin-left':'15px', 'margin-top':'15px', 'margin-right':'15px'}
            ),
            html.Div(
                children=[
                    html.H6('Choose which properties or offices to display:'),
                    dcc.Dropdown(
                        id=ids.OFFS_PROPS_DROPDOWN,
                        multi=True,
                        style={'overflowY': 'auto', 'max-height': '625px'}
                    ),
                    html.Button(
                        className="dropdown_button",
                        children=["Select All"],
                        style = {'margin-top':'10px'},
                        id=ids.SELECT_ALL,
                    )
                ], style = {'margin-left':'15px', 'margin-top':'15px', 'margin-right':'15px'}
            )
        ]
    )