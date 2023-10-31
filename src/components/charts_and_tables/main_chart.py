""" This file renders the chart that is depicted in the main tab of the
    dashboard """

from dash import Dash, dcc
from dash.dependencies import Input, Output
import plotly.express as px

import src.components.layout.ids as ids
from src.functions import makeStringsNice, all_data_dict

def prepFileForPlot(df, officeOrProp, offsOrPropsToKeep):
    df.fillna(0, inplace=True)
    df[officeOrProp] = df[officeOrProp].apply(makeStringsNice)
    df = df.T
    df.columns=df.iloc[0]
    df = df[1:]
    df = df.loc[:, df.columns.intersection(offsOrPropsToKeep)]
    return df

# usageOrSpending must be lowercase
def getPlot(g_or_e, u_or_s, officeOrProp, offsOrPropsToKeep):

    usageUnit = 'therms' if g_or_e=='gas' else 'kWh'
    unit = '$' if u_or_s=='spending' else usageUnit
    title_ge = 'Gas' if g_or_e=='gas' else 'Electricity'
    title_us = 'Usage' if u_or_s=='usage' else 'Spending'
    title_po = 'Property' if officeOrProp=='Property_Name' else 'Office'

    df = prepFileForPlot(all_data_dict[(g_or_e, u_or_s, officeOrProp)], officeOrProp, offsOrPropsToKeep)
    
    fig = px.line(df, x=df.index, y=df.columns)
    fig.update_layout(
        title={'text': 'Cook County ' + title_ge + ' ' + title_us + ' by ' + title_po,'x': 0.5},
        xaxis_title=None,
        yaxis_title=u_or_s + ' (' + unit + ')',
    )
    return fig

def render(app: Dash):
    @app.callback(
        Output(ids.CHART, 'children'),
        Input(ids.GAS_OR_ELEC, 'value'),
        Input(ids.USAGE_OR_SPENDING, 'value'),
        Input(ids.OFFICES_OR_PROPS, 'value'),
        Input(ids.OFFS_PROPS_DROPDOWN, 'value'),
    )
    def update_main_chart(gasOrElec: str, usageOrSpending: str, offsOrProps: str, offsOrPropsToKeep: list[str]):
        g_or_e = 'electricity' if gasOrElec=='Electricity' else 'gas'
        u_or_s = 'usage' if usageOrSpending=='Usage' else 'spending'
        o_or_p = 'Property_Name' if offsOrProps=='Property' else 'Office'

        fig = getPlot(g_or_e, u_or_s, o_or_p, offsOrPropsToKeep)
        fig = dcc.Graph(figure=fig)
        return fig