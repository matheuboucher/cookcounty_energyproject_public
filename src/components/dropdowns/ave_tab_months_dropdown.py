""" This file renders the dropdown that allows the user to decide which months
    to use to calculate the averages that are depicted in the averages tab of
    the dashboard """

from dash import Dash, html, dcc
from dash.dependencies import Input, Output
from src.functions import all_data_dict
import src.components.layout.ids as ids

e_s_p = all_data_dict['electricity', 'usage', 'Property_Name']
dates = e_s_p.columns.drop('Property_Name')
    
def render(app: Dash):

    @app.callback(
        Output(ids.DATES_DROPDOWN_AVE, "value"),
        Input(ids.DATES_SELECT_ALL, "n_clicks")
    )

    def select_all_dates(_: int):
        return dates

    return html.Div(
        children=[
            html.H6('Months Selected for Average'),
            dcc.Dropdown(
                options=dates,
                id=ids.DATES_DROPDOWN_AVE,
                multi=True,
            ),
            html.Button(
                className="dropdown_button",
                children=["Select All"],
                style = {'margin-top':'10px'},
                id=ids.DATES_SELECT_ALL,
            ),
        ],
    )