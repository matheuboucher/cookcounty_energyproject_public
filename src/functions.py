""" This file contains functions that read in electricity and gas
    spending and usage data from the electricity_data and gas_data folders
    in the data folder. These folders should contain files for 2021, 2022,
    and 2023. This file ultimately produces a dictionary containing all of the
    dataframes that are used in the charts_and_tables files to create the charts
    and tables that are depicted in the dashboard. """

from functools import reduce
import re
import pandas as pd

# Create a class for the Excel files that will contain the file, the sheet names
# in the file, and the year of the file to make accessing these items/values
# more efficient/simpler
class readEnergyExcelFiles:
    def __init__(self, filename):
        self.file = pd.read_excel('./data/' + filename + '.xlsx', sheet_name=None)
        self.sheets = list(self.file.keys())
        self.year = None
        match = re.search(r"\d{4}", filename)
        if match:
            self.year = f"{match.group()}"

## Get the excel files for 2021, 2022, 2023
ogElecFile21 = readEnergyExcelFiles('originalElectricity2021')
ogElecFile22 = readEnergyExcelFiles('originalElectricity2022')
ogElecFile23 = readEnergyExcelFiles('originalElectricity2023')

## Get the excel files for 2021, 2022, 2023
ogGasFile21 = readEnergyExcelFiles('originalGas2021')
ogGasFile22 = readEnergyExcelFiles('originalGas2022')
ogGasFile23 = readEnergyExcelFiles('originalGas2023')

# Get rid of chained assignment warnings
pd.set_option('mode.chained_assignment', None)

# This function removes possibly dangerous characters
# INPUT: String
# OUTPUT: String
def makeStringsNice(string):
    string = str(string)
    string = string.lower().strip()
    string = string.replace('-', '').replace(' ', '_').replace('.', '').replace('#', '').replace('&', '').replace('(', '').replace(')', '').replace('__', '_').replace('\'s', '')
    return string

# Extract lists of Cook County's properties and offices from the
# propertyNamesAndOffices Excel file
propNamesAndOffices = pd.read_excel('./propertyNamesAndOffices.xlsx')
propNamesAndOffices['Property_Name'] = propNamesAndOffices['Property_Name'].apply(makeStringsNice)
propNamesAndOffices['Office'] = propNamesAndOffices['Office'].apply(makeStringsNice)
properties = list(propNamesAndOffices['Property_Name'].unique())
offices = list(propNamesAndOffices['Office'].unique())

# This function takes in an Excel file processed using readEnergyExcelFiles
# above. It prepares the monthly sheets in the file for a merge by isolating the
# Property Name, kWh/therms, and Total Amount columns in each sheet and pivoting it
# to aggregate rows where 'Property Name' is the same, and appending it to the
# desiredSheetsList, which will be merged to create a yearly usage and spending df
# NOTE: Function only works for the 2022 and 2023 Gas/Electriciy Excel files
# INPUT: Pandas dataframe read from Excel file; string indicating the unit to be
#        used – kWh for electricity and therms for gas
# OUTPUT: List of dataframes containing each month's electricity and usage data
def addMonthsDataToList(excFile, string):
    listOfMonthsData = list()
    for sheet in excFile.sheets:
        if (((excFile.year + '-') in sheet) | ((str(int(excFile.year) - 1) + '-') in sheet)):

            month=sheet[-3:]
            year=sheet[0:4]

            dataframe=excFile.file[sheet]
            dataframe.columns=[c.replace(' ', '_') for c in dataframe.columns]

            # Drop entries that are na in the kWh/therms and property name columns
            dataframe[string] = pd.to_numeric(dataframe[string], errors='coerce')
            dataframe.dropna(axis=0, subset=(string, 'Property_Name'), inplace=True)
            dataframe['Property_Name'].fillna(dataframe['Service_Address'], inplace=True)
            dataframe['Property_Name'] = dataframe['Property_Name'].apply(makeStringsNice)
            columns_to_keep=['Property_Name', string, 'Total_Amount']
            columns_to_select = dataframe.columns.str.contains('|'.join(columns_to_keep), regex=True)
            df = dataframe[dataframe.columns[columns_to_select]]
            #df=dataframe.filter(regex=f'Property_Name|{string}|Total_Amount')

            # Convert columns explicitly to appropriate data types
            df['Property_Name'] = df['Property_Name'].astype(str)
            df[string] = df[string].astype(float)
            df['Total_Amount'] = df['Total_Amount'].astype(float)

            # Set property name as index before adding month suffix to other columns
            df.set_index('Property_Name', inplace=True)
            df=df.pivot_table(index='Property_Name').add_suffix(f'_{month}_{year}')
            df.reset_index(inplace=True)

            listOfMonthsData.append(df)
    return listOfMonthsData

# This function merges a list of dataframes containing usage and spending data for
# for each facility in Cook County, output by the above addMonthsDataToList
def mergeMonthsSheetsToYear(listOfMonthSheets):
    yearDf = reduce(lambda x, y: pd.merge(x, y, how='outer', on='Property_Name'), listOfMonthSheets)
    yearDf.fillna(0, inplace=True)
    return yearDf

# This function takes in two strings, gasOrElec, which denotes whether the
# the function is dealing with gas or electricity data, and officeOrProp, which
# denotes whether the data should be grouped by offices or properties
def aggregateYears(gasOrElec, officeOrProp):
    if gasOrElec=='gas':
        unit='therms'
        listOfYearlongDfs = [ogGasFile22, ogGasFile23]
    else:
        unit='kWh'
        listOfYearlongDfs = [ogElecFile22, ogElecFile23]

    # Months sheets for usage and spending 2022 and 2023
    months22 = addMonthsDataToList(listOfYearlongDfs[0], unit)
    months23 = addMonthsDataToList(listOfYearlongDfs[1], unit)

    # Dataframes containing usage and spending data for 2022 and 2023
    df22 = mergeMonthsSheetsToYear(months22)
    df23 = mergeMonthsSheetsToYear(months23)

    # Merging 2022 and 2023 dataframes, dropping duplicated columns
    # Adapted from code found on pauldesalvo.com
    df = pd.merge(df22, df23, how='outer', on='Property_Name', suffixes=('', '_drop'))
    df.drop([col for col in df.columns if 'drop' in col], axis=1, inplace=True)

    df = pd.merge(df, propNamesAndOffices, how='left', on='Property_Name')
    columns_to_keep=[officeOrProp, unit, 'Total_Amount']
    columns_to_select = df.columns.str.contains('|'.join(columns_to_keep), regex=True)
    df = df[df.columns[columns_to_select]]

    # If officeOrProp is 'Office', pivot the table to get the data grouped by
    # offices rather than properties
    if officeOrProp == 'Office':
        columns=list(df.columns)
        columns.insert(0, columns.pop(columns.index('Office')))
        df=df.pivot_table(index='Office', aggfunc='sum')
        df.reset_index(inplace=True)
        df = df[columns]

    # Dictionary containing one dataframe for usage and the other for spending
    usage = df.filter(regex=f'{officeOrProp}|{unit}')
    usage.columns = usage.columns.str.removeprefix(f'{unit}_')

    spending = df.filter(regex=f'{officeOrProp}|Total_Amount')
    spending.columns = spending.columns.str.removeprefix('Total_Amount_')

    # Dictionary containing dataframes for usage, spending, and combined
    usageSpendingDict = {
        'total' : df,
        'usage' : usage,
        'spending' : spending
    }
    return usageSpendingDict

# Combined usage and spending electricity data for Cook County offices
elec_offices = aggregateYears('electricity', 'Office')['total']['Office']
# Combined usage and spending gas data for Cook County offices
gas_offices = aggregateYears('gas', 'Office')['total']['Office']

# Combined usage and spending electricity data for Cook County facilities
elec_properties = aggregateYears('electricity', 'Property_Name')['total']['Property_Name']
# Combined usage and spending gas data for Cook County facilities
gas_properties = aggregateYears('gas', 'Property_Name')['total']['Property_Name']

# Electricity usage data for Cook County facilities
elec_usage_props = aggregateYears('electricity', 'Property_Name')['usage']
# Electricity usage data for Cook County offices
elec_usage_offs = aggregateYears('electricity', 'Office')['usage']

# Electricity spending data for Cook County facilities
elec_spend_props = aggregateYears('electricity', 'Property_Name')['spending']
# Electricity spending data for Cook County offices
elec_spend_offs = aggregateYears('electricity', 'Office')['spending']

# Gas usage data for Cook County facilities
gas_usage_props = aggregateYears('gas', 'Property_Name')['usage']
# Gas usage data for Cook County offices
gas_usage_offs = aggregateYears('gas', 'Office')['usage']

# Gas spending data for Cook County facilities
gas_spend_props = aggregateYears('gas', 'Property_Name')['spending']
# Gas spending data for Cook County offices
gas_spend_offs = aggregateYears('gas', 'Office')['spending']

# Dictionary containing all eight of the electricity and gas spending and usage
# dataframes to be accessed 
all_data_dict = {
    ('electricity', 'usage', 'Property_Name'): elec_usage_props,
    ('electricity', 'usage', 'Office'): elec_usage_offs,
    ('electricity', 'spending', 'Property_Name'): elec_spend_props,
    ('electricity', 'spending', 'Office'): elec_spend_offs,
    ('gas', 'usage', 'Property_Name'): gas_usage_props,
    ('gas', 'usage', 'Office'): gas_usage_offs,
    ('gas', 'spending', 'Property_Name'): gas_spend_props,
    ('gas', 'spending', 'Office'): gas_spend_offs,
}

# Sorted list of Cook County facilities
properties = sorted(properties)
# Sorted list of Cook County Offices
offices = sorted(offices)