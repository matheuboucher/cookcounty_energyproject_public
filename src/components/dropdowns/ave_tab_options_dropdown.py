""" This file renders the dropdown that allows the user to decide whether to
    group the data that will be used in the averages tab of the dashboard 
    by facilities or offices. """

from dash import Dash, html, dcc
from dash.dependencies import Input, Output
import src.components.layout.ids as ids
from src.functions import properties, offices

def render(app: Dash):

    @app.callback(
        Output(ids.OP_DROPDOWN_AVE, 'value'),
        Output(ids.OP_DROPDOWN_AVE, 'options'),
        Output(ids.AVE_OFFICE_SELECTED_TITLE, 'children'),
        Input(ids.O_OR_P_AVE, 'value')
    )
    def update_output(offsOrProps):
        output_title = 'Select ' + offsOrProps
        value = properties if offsOrProps=="Property" else offices
        init_val = value[0]
        options = [{'label': val, 'value': val} for val in value]
        return init_val, options, output_title

    return html.Div(
        children=[
            html.H6(id=ids.AVE_OFFICE_SELECTED_TITLE),
            dcc.Dropdown(
                id=ids.OP_DROPDOWN_AVE,
                clearable=False,
            )
        ]
    )
    