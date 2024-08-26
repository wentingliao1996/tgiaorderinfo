import pygsheets
import pandas as pd
import plotly.graph_objects as go


def is_number_or_text(value):
    if pd.isna(value):
        return False
    if isinstance(value, (int, float)):
        return True
    if isinstance(value, str):
        return value.strip() != ""
    return False
def get_df():
    gc = pygsheets.authorize(service_file ='googleAPI.json')
    google_sheet = gc.open_by_url('https://docs.google.com/spreadsheets/d/YOURGOOGLESHEERID/')
    worksheet = google_sheet.worksheet_by_title('Info.')
    df = worksheet.get_as_df()
    df.columns =['# ',
     'Work Sheet',
     'Urgent',
     'Entry Date',
     'Due Date',
     'Salesperson',
     'PO#',
     '1st Outsource',
     '',
     '',
     '2nd Outsource',
     '',
     '',
     'Unit',
     'User',
     'Job/\nProject',
     'Product/ Quantity',
     'Library\n(n)',
     'sample\n(n)',
     'Gb\n(Total)',
     'Application',
     'Sample\n(Type)',
     'Receive\n(Date)',
     'Sample QC\n收樣(Date)',
     'Sample QC\n收樣(Pass)',
     'Libray\n建庫(Date)',
     'Library QC\n建庫(Pass)',
     'Consent \nForm',
     'Sample\nReturn',
     '1st NGS',
     '1st Date',
     '1st Gb',
     '2nd NGS',
     '2st Date',
     '2nd Gb',
     '3rd NGS',
     '3st Date',
     '3rd Gb',
     '4th NGS',
     '4st Date',
     '4rd Gb',
     'NGS QC\nPass',
     'Analysis\nRequest',
     'Analysis\nProgress',
     'NAS',
     'End\n(Date)',
     'Data Path',
     'Report',
     'ERP\nWarehousing',
     'Data \nOutput',
     'Report \nOutput',
     'Contact\nPerson',
     'Contact E-mail',
     'TEL',
     'NGS Note1:\nLibrary info.',
     'NGS Note2:\nDeieverable Note',
     '']
    
    # df['Entry Date'] = pd.to_datetime(df['Entry Date'], errors='coerce')
    # df['Report \nOutput'] = pd.to_datetime(df['Report \nOutput'], errors='coerce')
    return df.dropna()

def count_times(df, year):
    filterdf = df[['PO#','Entry Date','1st Gb', '2nd Gb', '3rd Gb','4rd Gb']].iloc[6:]
    df2024 = filterdf[filterdf['Entry Date'].dt.year == year]
    count_dict = {}
    for column in df2024.columns[2:]:
        count_dict[column] = df2024[column].apply(is_number_or_text).sum()
    print(count_dict)
    return count_dict

def get_full_df(df):
    filtered_df = df[(df['Report \nOutput'].str.contains(r'\d', na=False)) & (df['Entry Date'].str.contains(r'\d', na=False))]
    filtered_df['Entry Date'] = pd.to_datetime(filtered_df['Entry Date'], errors='coerce')
    filtered_df['Report \nOutput'] = pd.to_datetime(filtered_df['Report \nOutput'], errors='coerce')
    filtered_df = filtered_df.dropna(subset=['Entry Date'])
    filtered_df = filtered_df[filtered_df['Entry Date'].dt.year != 2202]
    return filtered_df

def get_avage_ship_time(date_df):
    total_difference_days = date_df['Difference_days'].sum()
    total_rows = date_df.shape[0]
    average_difference_days = int(total_difference_days / total_rows)

    return average_difference_days

def filt_date_df(filtered_df):
    filtered_df['Difference'] =filtered_df['Report \nOutput'] - filtered_df['Entry Date']
    date_df = filtered_df[['Difference', 'Report \nOutput', 'Entry Date']]
    date_df['Difference_days'] = date_df['Difference'].dt.days
    date_df['Year'] = date_df['Entry Date'].dt.to_period('Y')
    date_df['Month'] = date_df['Entry Date'].dt.to_period('M')
    date_df['Case'] = 1


    return date_df

def get_count(df, unit):
    unit_counts = df.value_counts().reset_index()
    unit_counts.columns = [unit, 'Count']
    return unit_counts
    

def create_pie_df(unit_counts, unit):
    top_n = 10
    if len(unit_counts) > top_n:
        top_units = unit_counts[:top_n]
        others_count = unit_counts[top_n:]['Count'].sum()
        others_row = pd.DataFrame([['Others', others_count]], columns=[unit, 'Count'])
        unit_counts = pd.concat([top_units, others_row])
    return unit_counts
    
def get_all_count(data_df):
    data_df['Entry Date'] = pd.to_datetime(data_df['Entry Date'])

    # Extract only the month as an integer
    data_df['Month'] = data_df['Entry Date'].dt.month
    # Group by 'Year' and 'Month' to get the case count for each month and year
    month_stats = data_df.groupby(['Month', 'Year']).agg(
        case_count=('Difference', 'size'),
        total_shipping_days=('Difference', 'sum')
    )

    # Pivot the table to have 'Month' as rows and 'Year' as columns
    pivot_table = month_stats['case_count'].unstack().fillna('')
    return pivot_table

def get_module_data():
    gc = pygsheets.authorize(service_file ='googleAPI.json')
    google_sheet = gc.open_by_url('https://docs.google.com/spreadsheets/d/YOURGOOGLESHEERID/')
    worksheet = google_sheet.worksheet_by_title('案件資料')
    sampledf = worksheet.get_as_df()
    unreport = sampledf[(sampledf['定序進度'] != 'FINISH') & (sampledf['定序進度'] != 'DONE') & (sampledf['定序進度'] != 'CANCEL')& (sampledf['定序進度'] != 'NO REPORT')]

    return unreport

def get_unreport_status(unreport):
    count_df = unreport.groupby('定序進度').size().reset_index(name='Count')
    count_df = count_df.sort_values(by='Count', ascending=True)
    count_df['定序進度'].replace('', 'UNFILLED', inplace=True)
    count_df.columns = ["Status", "Count"]

    return count_df


def get_undone_df(df, current_year):
    # df = df.drop([0, 1,2,3,4,5])
    df['Entry Date'] = df['Entry Date'].astype(str)
    filter_df = df[(~df['Data \nOutput'].str.contains(r'\d', na=False)) & (df['Entry Date'].str.contains(r'\d', na=False))]
    filter_df['Entry Date'] = pd.to_datetime(filter_df['Entry Date'], errors='coerce')
    filter_df = filter_df[(filter_df['Data \nOutput']=='')&(filter_df['Work Sheet']!='')&(filter_df['Unit']!='TGIAR台基盟研發')]
    filter_df = filter_df[filter_df['Entry Date'].dt.year == int(current_year)]
    output_df = filter_df[['# ','PO#','Entry Date','Unit','User','Job/\nProject','Sample QC\n收樣(Pass)','Library QC\n建庫(Pass)','NGS QC\nPass','End\n(Date)','Data \nOutput']]
    output_df.columns=['#', 'PO#', 'Entry Date', 'Unit','User','Project','Sample QC','Library QC','NGS QC', 'Analyse End Date','Output Data']
    output_df = output_df.sort_values(by='#', ascending=False).reset_index(drop= True)
    return output_df

def get_ngs_count(df):
    column_list = ['1st Date','2st Date','3st Date','4st Date']

    for c in column_list:
        df[c] = pd.to_datetime(df[c], errors='coerce')
    daylist = ['Entry Date']+column_list
    NGS_count = df[daylist].dropna(subset=['1st Date'])
    NGS_count[column_list] = NGS_count[column_list].notna().astype(int)
    NGS_count['Entry Date'] = pd.to_datetime(NGS_count['Entry Date'], errors='coerce')
    NGS_count['Year'] = NGS_count['Entry Date'].dt.year
    NGS_count['Year'] = NGS_count['Year'].replace(2202, 2022)
    # 計算每個年份中非 NaT 值的個數
    count_df = NGS_count.groupby('Year')[column_list].sum().reset_index()
    count_df.columns = ['Year','1st NGS','2st NGS', '3st NGS', '4st NGS']
    return count_df

