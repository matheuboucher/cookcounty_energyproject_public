""" This file renders the table that is depicted in the main tab of the
    dashboard and updates that table based on the user's selections in the
    dropdowns. """

from dash import Dash, dash_table
from dash.dependencies import Input, Output
import src.components.layout.ids as ids
import src.functions as fcns

def render(app: Dash):
    @app.callback(
        Output(ids.TABLE, 'children'),
        Input(ids.OFFS_PROPS_DROPDOWN, 'value'),
        Input(ids.GAS_OR_ELEC, 'value'),
        Input(ids.USAGE_OR_SPENDING, 'value'),
        Input(ids.OFFICES_OR_PROPS, 'value')
    )
    def update_table(offsOrPropsToKeep: list[str], gasOrElec:str, usageOrSpending: str, offsOrProps):
        g_or_e = 'electricity' if gasOrElec=='Electricity' else 'gas'
        u_or_s = 'usage' if usageOrSpending=='Usage' else 'spending'
        o_or_p = 'Property_Name' if offsOrProps=='Property' else 'Office'

        df = fcns.all_data_dict[(g_or_e, u_or_s, o_or_p)]

        df[o_or_p] = df[o_or_p].apply(fcns.makeStringsNice)
        df = df.set_index(o_or_p)
        df = df.astype(float).round(2).reset_index()
        df.fillna(0, inplace=True)
        filtered_df = df[df[o_or_p].isin(offsOrPropsToKeep)]

        table = dash_table.DataTable(
            data=filtered_df.to_dict('records'),
            style_cell={
                'height': 'auto',
                'minWidth': '100px', 'width': '100px', 'maxWidth': '150px',
                'whiteSpace': 'normal',
                'textAlign': 'right',
                'textOverflow': 'ellipsis',
            },
            style_cell_conditional=[{
                'if': {'column_id': 'Office'}, 'textAlign': 'left', 'minWidth': '150px'},
                {
                'if': {'column_id': 'Property_Name'}, 'textAlign': 'left', 'minWidth': '150px'}
            ],
            style_table={'overflowY': 'scroll', 'overflowX': 'scroll'},
            page_size=17,
            style_header={'fontWeight': 'bold'},
            editable=False,
            sort_action='native',
            tooltip_data=[{o_or_p: {'value': str(value), 'type': 'markdown'}
                        for o_or_p, value in row.items()
                        } for row in df.to_dict('records')
        ])
        return table
