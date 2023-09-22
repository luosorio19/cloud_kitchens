# Imports
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import numpy as np
from streamlit_echarts import st_echarts
from streamlit_echarts import st_pyecharts
import pyecharts.options as opts
from pyecharts.charts import Bar


def data_load(file_name):
    data = pd.read_csv(file_name)
    return data

st.set_page_config(layout="wide")

# we load the data that was previously cleaned and grouped to calculate the metrics in 
# the data_cleaning notebook, data_facility contains information from orders merged with 
# labor to calculate processing revenue
data_orders= data_load('data_orders_grouped.csv')
data_labor = data_load('data_labor_clean.csv')
data_facility = data_load('data_facility.csv')

#we define functions to group the data which can be from orders, labor or facility,
#we create a fuction for each of the five metrics and return the data ready to be plot

# when set a parameter called data_filter which will allow to check the metrics by day, week or month
# the values it can take are 'date','week','month', by putting it in 'date' we have a day level calculation
def get_metric_one(date_filter):
    if date_filter != 'date':
        orders_ = data_orders.groupby([date_filter,'facility'])[['gmv','orders']].sum().reset_index()
        orders_.sort_values(by=['facility',date_filter])
        orders_grouped = orders_.groupby(['facility'])[['gmv','orders']].mean().reset_index()
    else:
        orders_grouped = data_orders.groupby(['facility'])[['gmv','orders']].mean().reset_index()
    
    orders_grouped['gmv']=orders_grouped['gmv'].apply(lambda x : round(x,2))
    orders_grouped['orders']=orders_grouped['orders'].apply(lambda x : round(x,2))

    return orders_grouped

def get_metric_two(date_filter):
    if date_filter != 'date':
        orders_ = data_orders.groupby([date_filter,'organization_name'])[['gmv','orders']].sum().reset_index()
        orders_.sort_values(by=['organization_name',date_filter])
        orders_grouped = orders_.groupby(['organization_name'])[['gmv','orders']].mean().reset_index()
    else:
        orders_grouped = data_orders.groupby(['organization_name'])[['gmv','orders']].mean().reset_index()
    
    orders_grouped['gmv']=orders_grouped['gmv'].apply(lambda x : round(x,2))
    orders_grouped['orders']=orders_grouped['orders'].apply(lambda x : round(x,2))

    return orders_grouped

def get_metric_three(operational_hours) :
    orders_facility = data_orders.groupby(['facility'])[['orders']].sum().reset_index()
    orders_facility['avg_orders_perhour'] = orders_facility['orders']/(operational_hours*39)
    orders_facility.sort_values(by=['avg_orders_perhour'],ascending=False, inplace=True)

    orders_facility['avg_orders_perhour']=orders_facility['avg_orders_perhour'].apply(lambda x : round(x,2))

    return orders_facility

def get_metric_four(date_filter):
    if date_filter != 'date':
        labor_ = data_labor.groupby([date_filter,'facility'])[['hours_staffed','labor_cost']].sum().reset_index()
        labor_.sort_values(by=['facility',date_filter])
        labor_grouped = labor_.groupby(['facility'])[['hours_staffed','labor_cost']].mean().reset_index()
        labor_grouped.sort_values(by=['labor_cost'],ascending=False, inplace=True)

    else :
        labor_grouped = data_labor.groupby(['facility'])[['hours_staffed','labor_cost']].mean().sort_values(by=['labor_cost'],ascending=False).reset_index()
    
    labor_grouped['hours_staffed']=labor_grouped['hours_staffed'].apply(lambda x : round(x,2))
    labor_grouped['labor_cost']=labor_grouped['labor_cost'].apply(lambda x : round(x,2))

    return labor_grouped 

def get_metric_five(date_filter):
    if date_filter != 'date':
        facility_ = data_facility.groupby([date_filter,'facility'])[['orders_processed_per_hour_staffed','processing_revenue']].sum().reset_index()
        facility_.sort_values(by=['facility',date_filter])
        facility_grouped = facility_.groupby(['facility'])[['orders_processed_per_hour_staffed','processing_revenue']].mean().reset_index()

    else :
        facility_grouped = data_facility.groupby(['facility'])[['orders_processed_per_hour_staffed','processing_revenue']].mean().reset_index()
    
    facility_grouped['orders_processed_per_hour_staffed']=facility_grouped['orders_processed_per_hour_staffed'].apply(lambda x : round(x,2))
    facility_grouped['processing_revenue']=facility_grouped['processing_revenue'].apply(lambda x : round(x,2))
    
    return facility_grouped 


####### DASHBOARD

st.title("Facilities Revenue Analysis")
st.header("Case Study")
st.subheader("Lucia Osorio, Sep 2023")

st.markdown(
    """
    <style>
    .metric-button {
        background-color: #0074D9;
        color: white;
        padding: 10px 20px;
        border: none;
        border-radius: 5px;
        font-size: 24px;
        text-align: center;
    }
    </style>
    """,
    unsafe_allow_html=True
)

total_facilities = len(list(data_orders.facility.unique()))  
st.button(f"Facilities: {round(total_facilities)}")

total_restaurants = len(list(data_orders.organization_name.unique()))  
st.button(f"Restaurants: {round(total_restaurants)}")

net_revenue = data_facility['net_revenue'].sum()
st.button(f"Net Revenue: $ {round(net_revenue)}")

net_revenue_o = data_facility['expected_net_revenue'].sum()
st.button(f"Net Revenue Optimized: $ {round(net_revenue_o)}")


# Top 5 Most Successful Restaurants
st.header('Top 5 Most Successful Restaurants')
st.write(data_orders.groupby(['organization_name'])[['gmv',
                   'orders']].sum().sort_values(by =['gmv'],ascending=False).reset_index().head(5))

data_two = get_metric_two(date_filter='date')

col1, col2 = st.columns(2)

# Graph 1: Average Number of orders per Restaurant
with col1:
    st.header('Average Number of Orders per Restaurant (Day Level)')
    options1 = {
        "xAxis": {
            "type": "category",
            "data": data_two['organization_name'].tolist()
        },
        "yAxis": {"type": "value"},
        "series": [{"data": data_two['orders'].tolist(), "type": "bar"}],
        "tooltip": {
            "trigger": "axis",
            "formatter": "{b}: {c}",
        },
    }
    st_echarts(options=options1, height="350px")

# Graph 2: Average GMV per Restaurant
with col2:
    st.header('Average GMV per Restaurant (Day Level)')
    options2 = {
        "xAxis": {
            "type": "category",
            "data": data_two['organization_name'].tolist()
        },
        "yAxis": {"type": "value"},
        "series": [{"data": data_two['gmv'].tolist(), "type": "bar"}],
        "tooltip": {
            "trigger": "axis",
            "formatter": "{b}: {c}",
        },
    }
    st_echarts(options=options2, height="350px")

# Graph 3: Average Number of orders per Restaurant
data_one = get_metric_one('date')
with col1:
    st.header('Average Number of Orders per Facility')
    options1 = {
        "xAxis": {
            "type": "category",
            "data": data_one['facility'].tolist()
        },
        "yAxis": {"type": "value"},
        "series": [{"data": data_one['orders'].tolist(), "type": "bar"}],
        "tooltip": {
            "trigger": "axis",
            "formatter": "{b}: {c}",
        },
    }
    st_echarts(options=options1, height="350px")

# Graph 4: Average GMV per Facility
with col2:
    st.header('Average GMV per Facility')
    options2 = {
        "xAxis": {
            "type": "category",
            "data": data_one['facility'].tolist()
        },
        "yAxis": {"type": "value"},
        "series": [{"data": data_one['gmv'].tolist(), "type": "bar"}],
        "tooltip": {
            "trigger": "axis",
            "formatter": "{b}: {c}",
        },
    }
    st_echarts(options=options2, height="350px")    

# Average Number of orders per hour for each facility

data_three = get_metric_three(11)

st.header('Average Number of orders per hour for each facility')
options2 = {
        "xAxis": {
            "type": "category",
            "data": data_three['facility'].tolist()
        },
        "yAxis": {"type": "value"},
        "series": [{"data": data_three['avg_orders_perhour'].tolist(), "type": "bar"}],
        "tooltip": {
            "trigger": "axis",
            "formatter": "{b}: {c}",
        },
    }
st_echarts(options=options2, height="350px")

data_four = get_metric_four('date')

# Graph 5: Average Labor Hour per Facility
with col1:
    st.header('Average Labor Hour per Facility')
    options1 = {
        "xAxis": {
            "type": "category",
            "data": data_four['facility'].tolist()
        },
        "yAxis": {"type": "value"},
        "series": [{"data": data_four['hours_staffed'].tolist(), "type": "bar"}],
        "tooltip": {
            "trigger": "axis",
            "formatter": "{b}: {c}",
        },
    }
    st_echarts(options=options1, height="350px")

# Graph 6: Average Labor cost per Facility
with col2:
    st.header('Average Labor cost per Facility')
    options2 = {
        "xAxis": {
            "type": "category",
            "data": data_four['facility'].tolist()
        },
        "yAxis": {"type": "value"},
        "series": [{"data": data_four['labor_cost'].tolist(), "type": "bar"}],
        "tooltip": {
            "trigger": "axis",
            "formatter": "{b}: {c}",
        },
    }
    st_echarts(options=options2, height="350px")

# OPLH AND PROCESSING REVENUE

data_five = get_metric_five('date')

# Graph 7: Average Orders Processed per Hour Staffed
with col1:
    st.header('Average Orders Processed per Hour Staffed')
    options1 = {
        "xAxis": {
            "type": "category",
            "data": data_five['facility'].tolist()
        },
        "yAxis": {"type": "value"},
        "series": [{"data": data_five['orders_processed_per_hour_staffed'].tolist(), "type": "bar"}],
        "tooltip": {
            "trigger": "axis",
            "formatter": "{b}: {c}",
        },
    }
    st_echarts(options=options1, height="350px")

# Graph 8: Average Processing Revenue per Facility
with col2:
    st.header('Average Processing Revenue per Facility')
    options2 = {
        "xAxis": {
            "type": "category",
            "data": data_five['facility'].tolist()
        },
        "yAxis": {"type": "value"},
        "series": [{"data": data_five['processing_revenue'].tolist(), "type": "bar"}],
        "tooltip": {
            "trigger": "axis",
            "formatter": "{b}: {c}",
        },
    }
    st_echarts(options=options2, height="350px")

# Net and Processing Revenue per Facility
st.header('Net and Processing Revenue per Facility')
st.write(data_facility.groupby(['facility'])[['processing_revenue','net_revenue']].sum().reset_index())

# Net and Processing Revenue per Date and Facility
st.header('Net and Processing Revenue per Date and Facility')
st.write(data_facility.groupby(['date','facility'])[['processing_revenue','net_revenue']].mean().reset_index())

# Overstaffing Days
st.header('Overstaffing Days')
st.write(data_facility.loc[data_facility['overstaffing_flag']==1])























