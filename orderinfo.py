# -*- coding: utf-8 -*-
"""
Created on Tue Aug 24 10:17:07 2021

@author: Andi5
"""
import streamlit as st
import time
import datetime
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from utils import *


st.set_page_config(page_title='TGIA - Order Info',  layout='wide', page_icon='images/favicon.ico')

#this is the header

st.image('images/logo.png', width=200)
st.markdown(
    """
    <style>
    .custom-markdown {
        margin-bottom: -30px;  
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Add markdown and title with the custom class applied to the markdown
st.markdown('<div class="custom-markdown">TGIA Bioinformatics Department Services</div>', unsafe_allow_html=True)
st.title("Order Information Compilation Report")
st.markdown(" **| website:** https://docs.google.com/spreadsheets/d/YOURGOOGLESHEERID ")

## Data

with st.spinner('Updating Report...'):
    
    #Metrics setting and rendering

    
    current_year = datetime.datetime.now().year
    lastyear = current_year-1
    current_year = str(current_year)
    lastyear = str(lastyear)
    oridf  = get_df()
    df = get_full_df(oridf)
    date_df = filt_date_df(df)
    yearlist = ['All']+list(df['Entry Date'].dt.year.unique())
    yearly_stats = date_df.groupby('Year').agg(
        case_count=('Difference', 'size'),
        total_shipping_days=('Difference', 'sum')
    )
    yearly_stats['avage_ship'] = yearly_stats['total_shipping_days']/yearly_stats['case_count']
    month_stats = date_df.groupby('Month').agg(
        case_count=('Difference', 'size'),
        total_shipping_days=('Difference', 'sum')
    )
    month_stats['avage_ship'] = month_stats['total_shipping_days']/month_stats['case_count']
    # st.selectbox('Select Time Range', yearlist, help = 'Select the time period for which you want to obtain information')
        
    # 數值化總共以及今年的數量
    m1, m2, m3, m4, m5, m6 = st.columns((1,1,1,1,1,1)) 

    average_difference_days=get_avage_ship_time(date_df)
    average_month_cases=len(date_df)/len(list(set(date_df['Month'])))
    current_year_month_cases = yearly_stats.loc[current_year]['case_count']/len(month_stats.loc[current_year])
    
    dm1 = yearly_stats.loc[current_year]['case_count']-yearly_stats.loc[lastyear]['case_count']
    dm2 = current_year_month_cases-(yearly_stats.loc[lastyear]['case_count']/len(month_stats.loc[lastyear]))
    dm3 = yearly_stats.loc[str(current_year)]['avage_ship'].days-yearly_stats.loc[str(lastyear)]['avage_ship'].days

    m1.metric(label ='Total Number of Cases to Date',value = int(len(df)))
    m2.metric(label ='Total Average Monthly',value = str(f"{average_month_cases:.2f}"))
    m3.metric(label ='Average Days to Ship',value = str(f"{average_difference_days:.2f}"))
    m4.metric(label = 'Number of Done Cases in This Year',value = yearly_stats.loc[current_year]['case_count'], delta = str(dm1)+' last year')
    m5.metric(label = 'Average Monthly Cases in This Year',value = str(f"{current_year_month_cases:.2f}"), delta = str(f"{dm2:.2f}"+' last year'))
    m6.metric(label = 'Days to Ship in This Year',value = yearly_stats.loc[str(current_year)]['avage_ship'].days, delta = str(dm3)+' last year')
    
    # 繪製案件數量折線圖
    plotmonth_stats = month_stats.reset_index()

    plotmonth_stats['Month'] = plotmonth_stats['Month'].astype(str)  # Convert to string

    fig = px.line(plotmonth_stats, x='Month', y='case_count', title='Monthly Done Case Count', markers=True)
    fig.update_layout(
        xaxis_title='Month',
        yaxis_title='Case Count',
        xaxis=dict(type='category'),  
        title_x=0.5,
        height=300 
    )

    st.plotly_chart(fig, use_container_width=True)

    ## 上機次數
    ngs_count = get_ngs_count(oridf)

    fig = make_subplots(rows=1, cols=3, shared_yaxes=True,
                    subplot_titles=[f"Year {int(year)}" for year in ngs_count['Year']],
                    horizontal_spacing=0.1)

    for i, year in enumerate(ngs_count['Year']):
        fig.add_trace(
            go.Funnel(
                y=['1st NGS','2st NGS', '3st NGS', '4st NGS'],
                x=[ngs_count.loc[i, '1st NGS'],ngs_count.loc[i, '2st NGS'], ngs_count.loc[i, '3st NGS'], ngs_count.loc[i, '4st NGS']],
                textinfo="value+percent previous",
                name=str(int(year))
            ),
            row=1, col=i+1
        )

    fig.update_layout(
        title_text="NGS Count Funnel by Year",
        title_x=0.5,
        showlegend=False,
        yaxis_title="Stage",
        xaxis_title="Value",
        template='seaborn'
    )


    for i, year in enumerate(ngs_count['Year']):
        fig.update_xaxes(title_text=f"{int(year)}", row=1, col=i+1)

    st.plotly_chart(fig, use_container_width=True)

    # 各類型圓餅圖
    g1, g2, g3 = st.columns((0.4,1,0.6))
    typelist = ['Unit','Application','Sample','Analysis']

    pietype = g1.selectbox('Select Type', typelist, help = 'Select the type of distribution')
    
    if pietype == 'Unit':
        column_name = 'Unit'

    if pietype == 'Application':
        column_name = 'Application'

    if pietype == 'Sample':
        column_name = 'Sample\n(Type)'

    if pietype == 'Analysis':
        column_name = 'Analysis\nRequest'

    unit_counts = get_count(df[df[column_name]!=''][column_name], pietype)
    pie_df = create_pie_df(unit_counts, pietype)
    
    fig = px.pie(pie_df, names=pietype, values='Count', template='seaborn', hole=0.6)
    fig.update_layout(
        title_text=f"{pietype} Distribution Chart",
        title_x=0,
        margin=dict(l=0, r=10, b=10, t=30),
        yaxis_title=None,
        xaxis_title=None
    )

    g2.plotly_chart(fig, use_container_width=True)
    
    with g3:
        st.dataframe(unit_counts, width=800)
    
    ## 各年份的完成案件數
    cw1, cw2 = st.columns((0.4, 1))
    
    with cw1:
        st.markdown("Number of Done Orders per Month over the Years")
        all_count_df = get_all_count(date_df)
        st.dataframe(all_count_df, width=400)
    
    fig = px.histogram(date_df, x="Month", y="Case",
             color='Year', barmode='group')
    fig.update_layout(
        title_text=f"Monthly Done Order Number Bar Chart",
        title_x=0,
        margin=dict(l=0, r=10, b=10, t=30)
        )
    cw2.plotly_chart(fig, use_container_width=True)

    

    ## 未填寫出貨日期的表格
    undone_df = get_undone_df(oridf, current_year)
    search_term = st.text_input("Search:", "")

    filtered_df = undone_df[undone_df.apply(lambda row: search_term.lower() in row.astype(str).str.lower().to_string(), axis=1)]

    fig = go.Figure(
        data=[go.Table(
            columnorder=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
            columnwidth=[8, 10, 10, 15, 10, 10, 10, 10, 10, 10, 10],
            header=dict(
                values=list(filtered_df.columns),
                font=dict(size=12, color='white'),
                fill_color='#264653',
                line_color='rgba(255,255,255,0.2)',
                align=['left', 'center'],
                height=20
            ),
            cells=dict(
                values=[filtered_df[K].tolist() for K in filtered_df.columns],
                font=dict(size=12),
                align=['left', 'center'],
                fill_color='lightgray',
                line_color='rgba(255,255,255,0.2)',
                height=20)
        )]                              
    )

    fig.update_layout(title_text="Orders without Output Date", title_font_color='#264653', title_x=0,
                    margin=dict(l=0, r=10, b=10, t=30), height=480)


    st.plotly_chart(fig, use_container_width=True)
    
       
with st.spinner('Report updated!'):
    time.sleep(1)     
    
# Performance Section  
    
with st.expander("Analysis report status"):
    with st.spinner('Updating Report...'):
        
        unreportdf = get_module_data()
        count_df = get_unreport_status(unreportdf)

        cu1, cu2 = st.columns((1.6, 1))
        
        fig = px.bar(count_df, 
                x='Count', 
                y='Status', 
                orientation='h',
                title='Precent Number of Records by Status',
                labels={'Count': 'Number of Records', 'Status': 'Status'})
        
        fig.update_traces(marker_color='#7A9E9F')
        fig.update_layout(height=300)  # 根據需求設置高度

        cu1.plotly_chart(fig, use_container_width=True)

        with cu2:
            st.metric(label ='Precent Number of Undone Report',value = int(unreportdf.shape[0]))
            count_df = count_df.sort_values(by='Count', ascending=False)
            fig = go.Figure(
                    data = [go.Table (columnorder = [0,1], columnwidth = [40,20],
                        header = dict(
                        values = list(count_df.columns),
                        font=dict(size=12, color = 'white'),
                        fill_color = '#264653',
                        align = 'left',
                        height=20
                        )
                    , cells = dict(
                        values = [count_df[K].tolist() for K in count_df.columns], 
                        font=dict(size=12),
                        align = 'left',
                        fill_color='#F0F2F6',
                        height=20))]) 
                
            fig.update_layout(title_text="Precent Number of Records by Status",title_font_color = '#264653',title_x=0,margin= dict(l=0,r=10,b=10,t=30), height=300)
                
            st.plotly_chart(fig, use_container_width=True)
    
    



        
# streamlit run orderinfo.py --server.port YOURPORT
        
        
        
        
        
        
        
        