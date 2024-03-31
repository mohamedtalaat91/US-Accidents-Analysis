# Import libraries
import pandas as pd 
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import folium
from folium.plugins import HeatMap
import streamlit as st
from zipfile import ZipFile

# reading the cleand and splited data 
# for the cleaning and feature engineering see the Notebook "Mid Project analysis"
zip_file_path = "mohamedtalaat91/US-Accidents-Analysis/Deployment/source/US_data_cleand.zip"
with ZipFile(zip_file_path, 'r') as zip_ref:
    zip_ref.extractall()
extracted_files = zip_ref.namelist()
csv_file_name = extracted_files[0] 
data = pd.read_csv(csv_file_name)

zip_file_path = r"E:\Epsilon AI\MID PROJECT\Deployment\Source\accidents_conditions.zip"
with ZipFile(zip_file_path, 'r') as zip_ref:
    zip_ref.extractall()
extracted_files = zip_ref.namelist()
csv_file_name = extracted_files[0] 
accidents_conditions = pd.read_csv(csv_file_name)
st.write(accidents_conditions)



# Severity Analysis
def show_severity():
    severity_df = pd.DataFrame(data['severity'].value_counts()).rename(columns={'index':'Severity', 'count':'Cases'})
    fig = go.Figure(go.Funnelarea(
        text = ["Severity - 2","Severity - 3", "Severity - 4", "Severity - 1"],
    values = severity_df.Cases,title= "the impact of accedint on the road"))
    return(fig)


def severity_map(severity):
    fig = px.scatter_mapbox(data[(data.severity).isin(severity)],lat='start_lat',lon= 'start_lng',zoom = 3,
                              hover_name='city',color = 'severity')
    fig.update_layout(mapbox_style="open-street-map")
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    return fig
# END of Severity Analysis


# Time Analysis
def time_analysis(category):
    if category == "Year":
        cat_col = "year"
        fig = px.bar(data, x=data[cat_col].value_counts().index, y=((data[cat_col].value_counts().values)/len(data)*100).round(2),
             title=category+" frequency",color = ((data[cat_col].value_counts().values)/len(data)*100).round(2),text_auto = True ,color_continuous_scale=px.colors.sequential.Emrld)
        fig.update_layout(xaxis_title=category,yaxis_title="Percentage")
        return fig
    elif category == "Month Name":
        cat_col = "month_name"
        fig = px.bar(data, x=data[cat_col].value_counts().index, y=((data[cat_col].value_counts().values)/len(data)*100).round(2),
             title=category+" frequency",color = ((data[cat_col].value_counts().values)/len(data)*100).round(2),text_auto = True ,color_continuous_scale=px.colors.sequential.Emrld)
        fig.update_layout(xaxis_title=category,yaxis_title="Percentage")      
        return fig
    elif category == "Day Name":
        cat_col = "day_name"
        fig = px.bar(data, x=data[cat_col].value_counts().index, y=((data[cat_col].value_counts().values)/len(data)*100).round(2),
             title=category+" frequency",color = ((data[cat_col].value_counts().values)/len(data)*100).round(2),text_auto = True ,color_continuous_scale=px.colors.sequential.Emrld)
        fig.update_layout(xaxis_title=category,yaxis_title="Percentage")
        return fig
    elif category == "Hour":
        cat_col = "hour"
        fig = px.bar(data, x=data[cat_col].value_counts().index, y=((data[cat_col].value_counts().values)/len(data)*100).round(2),
             title=category+" frequency",color = ((data[cat_col].value_counts().values)/len(data)*100).round(2),text_auto = True ,color_continuous_scale=px.colors.sequential.Emrld)
        fig.update_layout(xaxis_title=category,yaxis_title="Percentage")
        return fig
    elif category == "Season":
        cat_col = "season"
        fig = px.bar(data, x=data[cat_col].value_counts().index, y=((data[cat_col].value_counts().values)/len(data)*100).round(2),
             title=category+" frequency",color = ((data[cat_col].value_counts().values)/len(data)*100).round(2),text_auto = True ,color_continuous_scale=px.colors.sequential.Emrld)
        fig.update_layout(xaxis_title=category,yaxis_title="Percentage")
        return fig
    elif category == "Sunrise OR Sunset":
        cat_col = "sunrise_sunset"
        fig = px.bar(data, x=data[cat_col].value_counts().index, y=((data[cat_col].value_counts().values)/len(data)*100).round(2),
             title=category+" frequency",color = ((data[cat_col].value_counts().values)/len(data)*100).round(2),text_auto = True ,color_continuous_scale=px.colors.sequential.Emrld)
        line = px.line(data, x=data[cat_col].value_counts().index, y=((data[cat_col].value_counts().values)/len(data)*100).round(2))
        fig.add_trace(line.data[0])
        fig.update_layout(xaxis_title=category,yaxis_title="Percentage")
        return fig

def time_series (date_category, time_value,date_data=data, fig_num=1):
    date_category=date_category.replace(" OR ","_").replace(" ","_").lower()
    date_data = data[data[date_category].isin(time_value)]
    fig_year = px.pie(date_data,values=date_data.year.value_counts().values,names=date_data.year.value_counts().index,width=300,height=400,title="Accidents per year",color_discrete_sequence=px.colors.sequential.Emrld_r)
    fig_year.update_layout(title_x=0.5,title_y=0.9,xaxis_title="Year",yaxis_title="Number of Accidents")
    fig_season = px.pie(date_data,values=date_data.season.value_counts().values,names=date_data.season.value_counts().index,title="Accidents per season",width=300,height=400,color_discrete_sequence=px.colors.sequential.Emrld_r)
    fig_season.update_layout(title_x=0.5,title_y=0.9,xaxis_title="Season",yaxis_title="Number of Accidents")
    fig_month = px.bar(date_data,x=date_data.month_name.value_counts().index, y=((date_data.month_name.value_counts().values)/len(date_data)*100).round(2),text_auto=True,title="Accidents per month",width=400,height=400,color_discrete_sequence=px.colors.sequential.Emrld_r)
    fig_month.update_layout(title_x=0.5,title_y=0.9,xaxis_title="Month",yaxis_title="Number of Accidents")
    fig_day = px.bar(date_data, x=date_data.day_name.value_counts().index, y=((date_data.day_name.value_counts().values)/len(date_data)*100).round(2), text_auto=True,title="Accidents per day",width=400,height=400,color_discrete_sequence=px.colors.sequential.Emrld_r)
    fig_day.update_layout(title_x=0.5,title_y=0.9,xaxis_title="Day",yaxis_title="Number of Accidents")
    fig_hour = px.bar(date_data,  x=date_data.hour.value_counts().index, y=((date_data.hour.value_counts().values)/len(date_data)*100).round(2),text_auto=True,title="Accidents per hour",width=400,height=400,color_discrete_sequence=px.colors.sequential.Emrld_r)
    fig_hour.update_layout(title_x=0.5,title_y=0.9,xaxis_title="Hour",yaxis_title="Number of Accidents")
    fig_sun = px.pie(date_data,values=date_data.sunrise_sunset.value_counts().values,names=date_data.sunrise_sunset.value_counts().index,title="Accidents per sunrise or sunset",width=300,height=400,color_discrete_sequence=px.colors.sequential.Emrld_r)
    fig_sun.update_layout(title_x=0.5,title_y=0.9,xaxis_title="Sunrise or Sunset",yaxis_title="Number of Accidents")
    if fig_num == 1:
        return fig_year
    elif fig_num == 2:
        return fig_season
    elif fig_num == 3:
        return fig_month
    elif fig_num == 4:
        return fig_day
    elif fig_num == 5:
        return fig_hour
    elif fig_num == 6:
        return fig_sun



def time_selector (date_category):
    if date_category == "Year" :
        return data.year.value_counts().index.to_list()
    elif date_category == "Season" :
        return data.season.value_counts().index.to_list()
    elif date_category == "Month Name" :
        return data.month_name.value_counts().index.to_list()
    elif date_category == "Day Name" :
        return data.day_name.value_counts().index.to_list()
    elif date_category == "Hour" :
        return data.hour.value_counts().index.to_list()
    elif date_category == "Sunrise OR Sunset" :
        return data.sunrise_sunset.value_counts().index.to_list()   
# End of Time Analysis

# Weather Analysis
def weather_analysis(weather_category,data=data):
    weather_category_c=weather_category.replace(" ","_").lower().strip()
    fig = px.histogram(data,x=weather_category_c,text_auto=True,nbins=10, marginal = 'box',color_discrete_sequence=px.colors.sequential.Emrld_r)
    fig.update_layout(title=f"Accidents per {weather_category}",title_x=0.5,title_y=0.9,xaxis_title=weather_category,yaxis_title="Number of Accidents")
    return fig

def weather_distribution(weather_category,data=data):
    weather_category_c=weather_category.replace(" ","_").lower().strip()
    fig = px.box(data,x='weather_condition',y=weather_category_c ,color= 'weather_condition',color_discrete_sequence=px.colors.sequential.Emrld_r)
    fig.update_layout(title=f"Accidents per {weather_category}",title_x=0.5,title_y=0.9,xaxis_title="Weather Condition",yaxis_title=weather_category)
    return fig

def weather_occurance_per_year(time_value,data=data):
    date_data = data[data['year'].isin(time_value)]
    weather = date_data.groupby('weather_condition').size().nlargest(10) / len(date_data) * 100
    fig = px.bar(weather,x=weather.index,y=weather.values,text_auto=True,title = 'percentage of weather condition occurance',color_discrete_sequence=px.colors.sequential.Emrld_r)
    fig.update_layout(title_x=0.5,title_y=0.9,xaxis_title="Weather Condition",yaxis_title="Percentage of Accidents")
    return fig
# End of Weather Analysis

# Location Analysis
def location_analysis(location,num,sorting,data=data):
    location_c = location.replace(" ","_").lower().strip()
    if sorting == "Largest":
        largest= data.groupby(location_c).size().nlargest(num) / len(data) * 100
        fig =px.bar(largest,x=largest.index,y=largest.values,text_auto=True,title = 'Percentage of '+location+' occurance',color_discrete_sequence=px.colors.sequential.Emrld_r)
        fig.update_layout(title_x=0.5,title_y=0.9,xaxis_title=location,yaxis_title=f"Percentage of Accidents in each {location}")
        return fig
    elif sorting == "Smallest":
        smallest = data.groupby(location_c).size().nsmallest(num)
        fig =px.bar(smallest,x=smallest.index,y=smallest.values,text_auto=True,title = 'Percentage of '+location+' occurance',color_discrete_sequence=px.colors.sequential.Emrld_r)
        fig.update_layout(title_x=0.5,title_y=0.9,xaxis_title=location,yaxis_title=f"Percentage of Accidents in each {location}")
        return fig

def time_zone(data=data):
 
        timezone = data.groupby('timezone').size().sort_values(ascending=False) / len(data) * 100

        fig =  px.bar(timezone, x=timezone.index, y=timezone.values,text_auto= True,
        title="Percentage of Accidents per Timezone",color_discrete_sequence=px.colors.sequential.Emrld_r)
        fig.update_layout(xaxis_title="Timezone",yaxis_title="Percentage of Accidents",title_x=0.5,title_y=0.9)

        return fig

def time_zone_map(data=data):
    fig = px.scatter_mapbox(data, lat="start_lat", lon="start_lng",color='timezone', hover_name="city", hover_data=["city", "county","state", "country", "timezone"],
                               zoom=3, height=600)

    fig.update_layout(mapbox_style="open-street-map")
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})

    return fig
        
def create_heatmap(df_loc, latitude, longitude, zoom, tiles='OpenStreetMap'):
    """
    Generate a Folium Map with a heatmap of accident locations.
    """
    # Create a list of coordinates from the dataframe columns 'Start_Lat' and 'Start_Lng'
    heat_data = [[row['start_lat'], row['start_lng']] for index, row in df_loc.iterrows()]

    # Create a map centered around the specified coordinates
    world_map = folium.Map(location=[latitude, longitude], zoom_start=zoom, tiles=tiles)

    # Add the heatmap layer to the map
    HeatMap(heat_data).add_to(world_map)

    return world_map

def conditions(condition,accidents_conditions=accidents_conditions):
    condition_c = condition.replace(" ","_").lower().strip()
    condition_data = accidents_conditions[condition_c].value_counts()
    fig = px.pie(condition_data, values=condition_data.values, names=condition_data.index, title=f"Percentage of {condition} occurance",color_discrete_sequence=px.colors.sequential.Emrld_r)
    fig.update_layout(xaxis_title=condition ,yaxis_title="Percentage of Accidents",title_x=0.3,title_y=0.9)
    return fig
    



