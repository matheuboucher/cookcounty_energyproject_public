""" This file renders the table that is depicted in the averages tab of the
    dashboard """

from dash import Dash, html, dash_table
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import pandas as pd
from src.functions import all_data_dict
import src.components.layout.ids as ids

def prep_for_ave_table(df):
    new_df = df.T
    new_df.columns = new_df.iloc[0]
    new_df = new_df[1:]
    return new_df

def get_me_selected_slice(df, selected_office, month_range):
    if selected_office in df.columns:
        dataframe=df[selected_office].loc[month_range]
    else:
        dataframe=pd.DataFrame(0, index=month_range, columns=[selected_office])
    return dataframe

def render(app: Dash):
    @app.callback(
        Output(ids.AVE, "children"),
        Input(ids.O_OR_P_AVE, "value"),
        Input(ids.OP_DROPDOWN_AVE, "value"),
        Input(ids.DATES_DROPDOWN_AVE, "value")
    )

    def update_ave_table(offOrProp: str, selected_office, month_range):
        o_or_p = 'Property_Name' if offOrProp=='Property' else 'Office'

        E_SPEND_DATA = prep_for_ave_table(all_data_dict['electricity', 'spending', o_or_p].round(2))
        E_USAGE_DATA = prep_for_ave_table(all_data_dict['electricity', 'usage', o_or_p].round(2))
        G_SPEND_DATA = prep_for_ave_table(all_data_dict['gas', 'spending', o_or_p].round(2))
        G_USAGE_DATA = prep_for_ave_table(all_data_dict['gas', 'usage', o_or_p].round(2))

        es_sliced_df = get_me_selected_slice(E_SPEND_DATA, selected_office, month_range)
        eu_sliced_df = get_me_selected_slice(E_USAGE_DATA, selected_office, month_range)
        gs_sliced_df = get_me_selected_slice(G_SPEND_DATA, selected_office, month_range)
        gu_sliced_df = get_me_selected_slice(G_USAGE_DATA, selected_office, month_range)

        es_table = es_sliced_df.reset_index().iloc[::-1].round(2)
        eu_table = eu_sliced_df.reset_index().iloc[::-1].round(2)
        gs_table = gs_sliced_df.reset_index().iloc[::-1].round(2)
        gu_table = gu_sliced_df.reset_index().iloc[::-1].round(2)

        ## Rename the columns of each slice to reflect what they show ##
        def rename_office(df, new_name):
            c = df.columns[1]
            df.rename(columns={c: str(c)}, inplace=True)
            df.rename(columns={str(c): new_name}, inplace=True)

        rename_office(es_table, 'Electricity Spending ($)')
        rename_office(eu_table, 'Electricity Usage (kWh)')
        rename_office(gs_table, 'Gas Spending ($)')
        rename_office(gu_table, 'Gas Usage (therms)')

        ## Merge all four 'slices' into one dataframe that is used to calculate averages ##
        es_eu = pd.merge(es_table, eu_table, on="index", how="outer")
        es_eu_gs = pd.merge(es_eu, gs_table, on="index", how="outer")
        es_eu_gs_gu = pd.merge(es_eu_gs, gu_table, on="index", how="outer")

        es_eu_gs_gu.iloc[:, 1:] = es_eu_gs_gu.iloc[:, 1:].apply(pd.to_numeric)


        # Add mean row using df.loc
        averages = pd.DataFrame([es_eu_gs_gu.mean(numeric_only=True).values], columns=es_eu_gs_gu.mean(numeric_only=True).index)
        averages.reset_index()
        averages.loc[0, 'index'] = 'Average'

        es_eu_gs_gu.rename(columns={'index': 'Month'}, inplace=True)
        averages.rename(columns={'index': '-'}, inplace=True)

        ## Create dash datatable that shows the columns that will be averaged ##
        months_table = dash_table.DataTable(
            data=es_eu_gs_gu.to_dict('records'),
            columns=[{"name": 'Month', "id": 'Month', "type": "text"},
                     {"name": 'Electricity Spending ($)', "id": 'Electricity Spending ($)', "type": "numeric", "format": {'specifier': '$.2f'}},
                     {"name": 'Electricity Usage (kWh)', "id": 'Electricity Usage (kWh)', "type": "numeric", "format": {'specifier': '.2f'}},
                     {"name": 'Gas Spending ($)', "id": 'Gas Spending ($)', "type": "numeric", "format": {'specifier': '$.2f'}},
                     {"name": 'Gas Usage (therms)', "id": 'Gas Usage (therms)', "type": "numeric", "format": {'specifier': '.2f'}}],
            style_table={
                'overflowY': 'scroll',
            },
            editable=False,
            style_header={'fontWeight': 'bold'},
            page_size=len(month_range)),
        
        averages_table = dash_table.DataTable(
            data=averages.to_dict('records'),
            columns=[{"name": '-', "id": '-', "type": "text"},
                     {"name": 'Electricity Spending ($)', "id": 'Electricity Spending ($)', "type": "numeric", "format": {'specifier': '$.2f'}},
                     {"name": 'Electricity Usage (kWh)', "id": 'Electricity Usage (kWh)', "type": "numeric", "format": {'specifier': '.2f'}},
                     {"name": 'Gas Spending ($)', "id": 'Gas Spending ($)', "type": "numeric", "format": {'specifier': '$.2f'}},
                     {"name": 'Gas Usage (therms)', "id": 'Gas Usage (therms)', "type": "numeric", "format": {'specifier': '.2f'}}],
            style_table={
                'overflowY': 'scroll',
            },
            style_header={'fontWeight': 'bold'},
            editable=False),

        html_div = html.Div([dbc.Row(
            [
                dbc.Col(html.Div(className="ave_table", children=months_table), width=6),
                dbc.Col(html.Div(className="ave_table", children=averages_table), width=6),
            ], justify="evenly", style = {'margin-left':'15px', 'margin-top':'15px', 'margin-right':'15px'}),]),
        return html_div
