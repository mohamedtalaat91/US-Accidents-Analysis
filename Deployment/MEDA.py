# Import libraries
import pandas as pd 
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import folium
from datasist.structdata import detect_outliers
from sklearn.impute import SimpleImputer
from folium.plugins import HeatMap
import streamlit as st
from zipfile import ZipFile

# reading the cleand and splited data 
# read data
zip_file_path = r"E:\Epsilon AI\MID PROJECT\Deployment\source\US_Accidents_March23_analysis.zip"
with ZipFile(zip_file_path, 'r') as zip_ref:
    zip_ref.extractall()
extracted_files = zip_ref.namelist()
csv_file_name = extracted_files[0] 
data = pd.read_csv(csv_file_name)

def data_cleaning(data = data):
# convert column names to lowercase
    data.columns= data.columns.str.lower()

    # droping some columns that are not needed
    data.drop(['id','source','description','street','airport_code','wind_direction','precipitation(in)','civil_twilight','nautical_twilight','astronomical_twilight','wind_chill(f)','pressure(in)','weather_timestamp','zipcode'],axis=1,inplace=True)

    # spliting data into 'data about accident' and'accident conditions'
    accidents_conditions= data[['amenity','bump', 'crossing', 'give_way', 'junction', 'no_exit', 'railway','roundabout', 'station', 'stop', 'traffic_calming', 'traffic_signal','turning_loop']]

    data.drop(accidents_conditions.columns,axis=1,inplace=True)


    # conver to datetime
    data.start_time = pd.to_datetime(data.start_time,format='mixed')
    data.end_time = pd.to_datetime(data.end_time,format='mixed')


    '''why we have few records with distance = 0
    there is many accidents with no impact on the road and don't make a large disabled distance in the road   
    it's small accident , so the start and end coordinates are same   
    based on that we have a few missing values in end_lat , end_lng coulmns    
    so we will fill the missing values with start_lat , start_lng'''

    data['end_lat'].fillna(data['start_lat'], inplace=True)
    data['end_lng'].fillna(data['start_lng'], inplace=True)


    # convert to object
    data.start_lat = data.start_lat.astype(object)
    data.start_lng = data.start_lng.astype(object)
    data.end_lat = data.end_lat.astype(object)
    data.end_lng = data.end_lng.astype(object)

    ''''filling missing values
    in the following columns we will fill the missing values with median because of outliers'''
    imputer = SimpleImputer(missing_values=np.nan, strategy='median')
    data[['humidity(%)','visibility(mi)','wind_speed(mph)','temperature(f)']] = imputer.fit_transform(data[['humidity(%)','visibility(mi)','wind_speed(mph)','temperature(f)']])


    # detecting outliers and removing it
    idx = detect_outliers(data, 0,['temperature(f)','wind_speed(mph)'])
    data.drop(idx , inplace=True)
    #  removing outliers from visibility but not all of it only 0 to 50 will remain
    idx = data[(data['visibility(mi)']<0) | (data['visibility(mi)']>50)].index
    data.drop(idx,inplace= True)

    '''filling timezone missing values
    sorting data by the longtude which is the time zone is sorted by 
    starting from the lowest (US_Pacific) to the highest (US_Estern)'''
    data.sort_values(by= 'start_lng',inplace=True)
    data.timezone.ffill(inplace=True)

    '''filling missing values with ffill  
    we will fill the missing values with ffill because this is a time series data 
    and we need to fill the missing values with the previous value    
    it's logicaly more accurate'''
    data.sort_values(by='start_time',inplace=True)
    data.sunrise_sunset.ffill(inplace=True)
    data.weather_condition.ffill(inplace = True)


    # droping remaining missing values and duplicates
    data.dropna(inplace=True)

    data.drop_duplicates(inplace=True)

    data.reset_index(drop=True, inplace=True)


    return data,accidents_conditions
data,accidents_conditions = data_cleaning(data)


data['year'] = data['start_time'].dt.year
data['month_name'] = data['start_time'].dt.month_name()
data['day_name'] = data['start_time'].dt.day_name()
data['hour'] = data['start_time'].dt.hour
data['duration'] = data['end_time']-data['start_time']

idx = data[data.duration.dt.days >1].index
data.drop(idx , inplace=True)

data.duration = data.duration.dt.total_seconds() / 3600

def get_season(x):
    if x in ['December', 'January', 'February']:
        return 'Winter'
    elif x in ['March','April','May']:
        return 'Spring'
    elif x in ['June','July','August']:
        return 'Summer'
    elif x in ['September','October','November']:
        return 'Autumn'


data['season'] = data['month_name'].apply(get_season)

data['distance(km)'] = data['distance(mi)']*1.60934
data.drop(['distance(mi)'],axis=1,inplace=True)

data['temperature(c)']= (data['temperature(f)']-32)*5/9
data.drop(['temperature(f)'],axis=1,inplace=True)

data['visibility(km)'] = data['visibility(mi)']*1.60934
data.drop(['visibility(mi)'],axis=1,inplace=True)

data['wind_speed(kmh)'] = data['wind_speed(mph)']*1.60934
data.drop(['wind_speed(mph)'],axis=1,inplace=True)

def categorize_weather(condition):
    condition = condition.lower()
    if 'clear' in condition or 'fair' in condition :
        return 'Clear'
    elif 'cloud' in condition or 'overcast' in condition or 'partly' in condition or 'scattered' in condition:
        return 'Cloudy'
    elif 'rain' in condition or 'drizzle' in condition or 'showers' in condition:
        return 'Rain'
    elif 'snow' in condition or 'sleet' in condition or 'ice pellets' in condition:
        return 'Snow'
    elif 'fog' in condition or 'mist' in condition or 'haze' in condition:
        return 'Fog/Mist/Haze'
    elif 'storm' in condition or 'thunder' in condition or 't-storm' in condition or 'tornado' in condition:
        return 'Storm'
    elif 'freezing' in condition:
        return 'Freezing'
    else:
        return 'Other'

data['weather_condition'] = data['weather_condition'].apply(categorize_weather)

columns_order = ['severity', 'start_time', 'end_time','duration','hour',
       'day_name', 'month_name', 'year' ,'season', 'start_lat', 'start_lng', 'end_lat', 'end_lng','timezone','distance(km)', 'city','county','state','country', 'temperature(c)','humidity(%)', 'visibility(km)', 'wind_speed(kmh)', 'weather_condition', 'sunrise_sunset']
data = data.reindex(columns=columns_order)





# Start of Analysis

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
        
def create_heatmap(df_loc=data, latitude=39.8283, longitude=-98.5795, zoom=4, tiles='OpenStreetMap'):
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
