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
from sklearn.model_selection import train_test_split

# reading the cleand and splited data 
# read data
zip_file_path = (r"./Deployment/source/US_Accidents_March23_analysis.zip")
with ZipFile(zip_file_path, 'r') as zip_ref:
    zip_ref.extractall()
extracted_files = zip_ref.namelist()
csv_file_name = extracted_files[0] 
data = pd.read_csv(csv_file_name)
data_droped,data= train_test_split(data,test_size= 0.5,random_state = 42)

'''----------------------------------------------------data cleaning--------------------------------------------------------'''


def data_cleaning(data = data):
    """
    This function is for data cleaning and preprocessing
    it takes a pandas DataFrame as input
    and return two DataFrames as output
    first DataFrame is about the accidents
    second DataFrame is about the accident conditions
    """

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

    '''filling missing values
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


'''----------------------------------------------------preprocessing--------------------------------------------------------'''

# creating new columns from datetime
data['year'] = data['start_time'].dt.year
data['month_name'] = data['start_time'].dt.month_name()
data['day_name'] = data['start_time'].dt.day_name()
data['hour'] = data['start_time'].dt.hour
data['duration'] = data['end_time']-data['start_time']

idx = data[data.duration.dt.days >1].index
data.drop(idx , inplace=True)

data.duration = data.duration.dt.total_seconds() / 3600

def get_season(x):
    ''' creating new season column '''
    if x in ['December', 'January', 'February']:
        return 'Winter'
    elif x in ['March','April','May']:
        return 'Spring'
    elif x in ['June','July','August']:
        return 'Summer'
    elif x in ['September','October','November']:
        return 'Autumn'
data['season'] = data['month_name'].apply(get_season)

# converting units
data['distance(km)'] = data['distance(mi)']*1.60934
data.drop(['distance(mi)'],axis=1,inplace=True)

data['temperature(c)']= (data['temperature(f)']-32)*5/9
data.drop(['temperature(f)'],axis=1,inplace=True)

data['visibility(km)'] = data['visibility(mi)']*1.60934
data.drop(['visibility(mi)'],axis=1,inplace=True)

data['wind_speed(kmh)'] = data['wind_speed(mph)']*1.60934
data.drop(['wind_speed(mph)'],axis=1,inplace=True)

def categorize_weather(condition):
    """
    This function takes a string input which represents weather condition
    and returns a categorized weather condition

    The function lowercases the input and checks if it contains any of the following words
    'clear' , 'fair' , 'cloud' , 'overcast' , 'partly' , 'scattered' , 'rain' , 'drizzle' , 'showers'
    , 'snow' , 'sleet' , 'ice pellets' , 'fog' , 'mist' , 'haze' , 'storm' , 'thunder' , 't-storm' , 'tornado' , 'freezing'

    If the input contains any of the above words the function returns one of the following categorized weather conditions
    'Clear' , 'Cloudy' , 'Rain' , 'Snow' , 'Fog/Mist/Haze' , 'Storm' , 'Freezing' , 'Other'

    If the input does not contain any of the above words the function returns 'Other'
    """
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

# reordering columns
columns_order = ['severity', 'start_time', 'end_time','duration','hour',
       'day_name', 'month_name', 'year' ,'season', 'start_lat', 'start_lng', 'end_lat', 'end_lng','timezone','distance(km)', 'city','county','state','country', 'temperature(c)','humidity(%)', 'visibility(km)', 'wind_speed(kmh)', 'weather_condition', 'sunrise_sunset']
data = data.reindex(columns=columns_order)





# Start of Analysis

# Severity Analysis
def show_severity():
    """
    This function calculates the number of cases for each severity level
    and creates a funnel plot to visualize the relationship between severity and cases.

    Returns:
        A Plotly figure object.
    """
    severity_df = pd.DataFrame(data['severity'].value_counts()).rename(columns={'index':'Severity', 'count':'Cases'})

    # create a funnel plot to show the relationship between severity and cases
    fig = go.Figure(go.Funnelarea(
        text = ["Severity - 2","Severity - 3", "Severity - 4", "Severity - 1"],
        values = severity_df.Cases,title= "the impact of accidents on the road"))
    return(fig)



def severity_map(severity):
    """
    This function creates a mapbox plot of accidents based on their severity level.
    It takes in a list of severity levels as an argument and filters the data based on it.

    Parameters:
        severity (list): A list of severity levels e.g. ['Severity - 2', 'Severity - 3']

    Returns:
        A Plotly figure object.
    """
    fig = px.scatter_mapbox(data[(data.severity).isin(severity)],lat='start_lat',lon= 'start_lng',zoom = 3,
                              hover_name='city',color = 'severity')
    fig.update_layout(mapbox_style="open-street-map")
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})

    return fig

# END of Severity Analysis


# Time Analysis
def time_analysis(category: str) -> go.Figure:
    """
    This function calculates the percentage of accidents based on a given time category
    (e.g. year, month, day, etc.) and plots it as a bar chart.

    Parameters:
        category (str): The category to group the data by (e.g. year, month, day, etc.)

    Returns:
        A Plotly figure object.
    """
    cat_col = category.lower().replace(" ", "_")
    df = data[cat_col].value_counts().reset_index()
    df.columns = [cat_col, 'count']
    df['percentage'] = (df['count'] / len(data) * 100).round(2)

    fig = px.bar(df, x=cat_col, y='percentage', title=f"{category} frequency",
                 color='percentage', text_auto=True, color_continuous_scale=px.colors.sequential.Emrld)

    fig.update_layout(xaxis_title=category, yaxis_title="Percentage")

    if category == "Sunrise OR Sunset":
        line = px.line(df, x=cat_col, y='percentage')
        fig.add_trace(line.data[0])

    return fig

def time_series (date_category, time_value,date_data=data, fig_num=1):
    """
    This function generates a pie chart or bar plot based on a given time category (e.g. year, season, month, day, hour, etc.)
    and a list of values of that category.

    Parameters:
        date_category (str): The category to group the data by (e.g. year, season, month, day, hour, etc.)
        time_value (list): A list of values of the date_category to generate the chart for.
        date_data (DataFrame): The data to generate the chart from. Defaults to the global 'data' variable.
        fig_num (int): The number of the chart to generate (1-6). Defaults to 1.

    Returns:
        A Plotly figure object.
    """
    date_category=date_category.replace(" OR ","_").replace(" ","_").lower()
    date_data_temp = date_data[date_data[date_category].isin(time_value)]
    if fig_num == 1:
        # Accidents per year
        fig = px.pie(date_data_temp,values=date_data_temp.year.value_counts().values,names=date_data_temp.year.value_counts().index,width=300,height=400,title="Accidents per year",
                     color_discrete_sequence=px.colors.sequential.Emrld_r)
    elif fig_num == 2:
        # Accidents per season
        fig = px.pie(date_data_temp,values=date_data_temp.season.value_counts().values,names=date_data_temp.season.value_counts().index,title="Accidents per season",
                     width=300,height=400,color_discrete_sequence=px.colors.sequential.Emrld_r)
    elif fig_num == 3:
        # Accidents per month
        fig = px.bar(date_data_temp,x=date_data_temp.month_name.value_counts().index, y=((date_data_temp.month_name.value_counts().values)/len(date_data_temp)*100).round(2),
                     text_auto=True,title="Accidents per month",width=400,height=400,color_discrete_sequence=px.colors.sequential.Emrld_r)
    elif fig_num == 4:
        # Accidents per day
        fig = px.bar(date_data_temp, x=date_data_temp.day_name.value_counts().index, y=((date_data_temp.day_name.value_counts().values)/len(date_data_temp)*100).round(2),
                     text_auto=True,title="Accidents per day",width=400,height=400,color_discrete_sequence=px.colors.sequential.Emrld_r)
    elif fig_num == 5:
        # Accidents per hour
        fig = px.bar(date_data_temp,  x=date_data_temp.hour.value_counts().index, y=((date_data_temp.hour.value_counts().values)/len(date_data_temp)*100).round(2),
                     text_auto=True,title="Accidents per hour",width=400,height=400,color_discrete_sequence=px.colors.sequential.Emrld_r)
    elif fig_num == 6:
        # Accidents per sunrise or sunset
        fig = px.pie(date_data_temp,values=date_data_temp.sunrise_sunset.value_counts().values,names=date_data_temp.sunrise_sunset.value_counts().index,
                     title="Accidents per sunrise or sunset",width=300,height=400,color_discrete_sequence=px.colors.sequential.Emrld_r)
    fig.update_layout(title_x=0.5,title_y=0.9)
    return fig





def time_selector(date_category):
    """
    Returns a list of all unique values of a given date category (e.g. year, month, day, etc.).

    Parameters:
        date_category (str): The category to get unique values for (e.g. year, month, day, etc.).

    Returns:
        A list of all unique values of the given date category.
    """

    # Replace spaces with underscores and make everything lowercase
    date_category = date_category.replace(" OR ", "_").replace(" ", "_").lower()

    # Get a pandas Series containing all unique values of the given date category
    date_category_counts = data[date_category].value_counts()

    # Return a list of all unique values of the given date category
    return date_category_counts.index.to_list()
# End of Time Analysis

# Weather Analysis
def weather_analysis(weather_category,data=data):
    """
    Generates a histogram of a given weather category (e.g. temperature, humidity, wind speed, etc.).

    Parameters:
        weather_category (str): The weather category to generate the histogram for (e.g. temperature, humidity, wind speed, etc.).
        data (DataFrame): The data to generate the histogram from. Defaults to the global 'data' variable.

    Returns:
        A Plotly figure object.
    """
    weather_category_c=weather_category.replace(" ","_").lower().strip()
    fig = px.histogram(data,x=weather_category_c,text_auto=True,nbins=10, marginal = 'box',color_discrete_sequence=px.colors.sequential.Emrld_r)
    fig.update_layout(title=f"Accidents per {weather_category}",# Add title to the plot
                       title_x=0.5, # Align the title to the center of the plot
                       title_y=0.9, # Move the title up a bit from the default position
                       xaxis_title=weather_category, # Add axis label for the x-axis
                       yaxis_title="Number of Accidents") # Add axis label for the y-axis
    return fig

def weather_distribution(weather_category, data=data):
    """
    Generates a box plot showing the distribution of a given weather category (e.g. temperature, humidity, wind speed, etc.) per weather condition.

    Parameters:
        weather_category (str): The weather category to generate the histogram for (e.g. temperature, humidity, wind speed, etc.).
        data (DataFrame): The data to generate the histogram from. Defaults to the global 'data' variable.

    Returns:
        A Plotly figure object.
    """

    # Replace spaces with underscores and make everything lowercase
    weather_category_c = weather_category.replace(" ", "_").lower().strip()

    # Generate the box plot
    fig = px.box(data, x='weather_condition', y=weather_category_c, color='weather_condition', color_discrete_sequence=px.colors.sequential.Emrld_r)

    # Add title to the plot
    fig.update_layout(
        title=f"Accidents per {weather_category}",
        title_x=0.5,  # Align the title to the center of the plot
        title_y=0.9,  # Move the title up a bit from the default position
        xaxis_title="Weather Condition",  # Add axis label for the x-axis
        yaxis_title=weather_category  # Add axis label for the y-axis
    )

    return fig

def weather_occurance_per_year(time_value, data=data):
    """
    Generates a bar plot showing the percentage of weather conditions that occur
    for a given list of years.

    Parameters:
        time_value (list): A list of years to generate the plot for.
        data (DataFrame): The data to generate the plot from. Defaults to the global 'data' variable.

    Returns:
        A Plotly figure object.
    """

    # Filter the data to the given list of years
    date_data = data[data['year'].isin(time_value)]

    # Group the data by weather condition and count the number of occurrences
    weather = date_data.groupby('weather_condition').size().nlargest(10) / len(date_data) * 100

    # Generate the bar plot
    fig = px.bar(weather, x=weather.index, y=weather.values, text_auto=True,
                 title='Percentage of weather condition occurance',
                 color_discrete_sequence=px.colors.sequential.Emrld_r)

    # Add title to the plot
    fig.update_layout(
        title_x=0.5,  # Align the title to the center of the plot
        title_y=0.9,  # Move the title up a bit from the default position
        xaxis_title="Weather Condition",  # Add axis label for the x-axis
        yaxis_title="Percentage of Accidents"  # Add axis label for the y-axis
    )

    return fig

# End of Weather Analysis

# Location Analysis
def location_analysis(location, num, sorting, data=data):
    """
    Generates a bar plot showing the percentage of location occurance in each category.

    Parameters:
        location (str): The location to generate the plot for (e.g. city, state, country, etc.).
        num (int): The number of locations to include in the plot.
        sorting (str): Either "Largest" or "Smallest" to determine which locations are included in the plot.
        data (DataFrame): The data to generate the plot from. Defaults to the global 'data' variable.

    Returns:
        A Plotly figure object.
    """

    location_c = location.replace(" ", "_").lower().strip()

    if sorting == "Largest":
        # Get the largest locations based on the number of accidents
        largest = data[location_c].value_counts().head(num)
        # Calculate the percentage of accidents that occurred in each location
        largest = largest / len(data) * 100
        # Generate the bar plot
        fig = px.bar(largest, x=largest.index, y=largest.values, text_auto=True, title=f'Percentage of {location} occurance',
                     color_discrete_sequence=px.colors.sequential.Emrld_r)
        # Add title to the plot
        fig.update_layout(
            title_x=0.5,  # Align the title to the center of the plot
            title_y=0.9,  # Move the title up a bit from the default position
            xaxis_title=location,  # Add axis label for the x-axis
            yaxis_title=f"Percentage of Accidents in each {location}"  # Add axis label for the y-axis
        )

    elif sorting == "Smallest":
        # Get the smallest locations based on the number of accidents
        smallest = data[location_c].value_counts().tail(num)
        # Calculate the percentage of accidents that occurred in each location
        smallest = smallest / len(data) * 100
        # Generate the bar plot
        fig = px.bar(smallest, x=smallest.index, y=smallest.values, text_auto=True,
                     title=f'Percentage of {location} occurance', color_discrete_sequence=px.colors.sequential.Emrld_r)
        # Add title to the plot
        fig.update_layout(
            title_x=0.5,  # Align the title to the center of the plot
            title_y=0.9,  # Move the title up a bit from the default position
            xaxis_title=location,  # Add axis label for the x-axis
            yaxis_title=f"Percentage of Accidents in each {location}"  # Add axis label for the y-axis
        )

    return fig



def time_zone(data=data):
    """
    This function calculates the percentage of accidents per time zone
    and generates a bar chart based on it.

    Parameters:
        data (DataFrame): The data to generate the chart from. Defaults to the global 'data' variable.

    Returns:
        A Plotly figure object.
    """
    timezone = data['timezone'].value_counts().sort_values(ascending=False) / len(data)

    fig =  px.bar(timezone, x=timezone.index, y=timezone.values,text_auto= True,  # Add the values of each category as hover text
                  title="Percentage of Accidents per Timezone",  # Add title to the plot
                  color_discrete_sequence=px.colors.sequential.Emrld_r)  # Color the bars
    fig.update_layout(
        xaxis_title="Timezone",  # Add axis label for the x-axis
        yaxis_title="Percentage of Accidents",  # Add axis label for the y-axis
        title_x=0.5,  # Align the title to the center of the plot
        title_y=0.9  # Move the title up a bit from the default position
    )

    return fig



def time_zone_map(data=data):
    """
    This function generates a mapbox plot of accidents based on their location.
    It takes in a DataFrame as an argument and plots it based on the 'start_lat' and 'start_lng' columns.

    Parameters:
        data (DataFrame): The data to generate the chart from. Defaults to the global 'data' variable.

    Returns:
        A Plotly figure object.
    """
    fig = px.scatter_mapbox(data, lat="start_lat", lon="start_lng", color_continuous_scale="RdYlGn",color_continuous_midpoint=0,
                               zoom=3, height=600, hover_name="city", hover_data=["city", "county","state", "country"])

    fig.update_layout(mapbox_style="open-street-map")
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})

    return fig


        
def create_heatmap(df_loc=data, latitude=39.8283, longitude=-98.5795, zoom=4, tiles='OpenStreetMap'):
    """
    Generate a Folium Map with a heatmap of accident locations.

    Parameters:
        df_loc (DataFrame): The data to generate the chart from. Defaults to the global 'data' variable.
        latitude (float): The latitude to center the map on. Defaults to 39.8283.
        longitude (float): The longitude to center the map on. Defaults to -98.5795.
        zoom (int): The zoom level for the map. Defaults to 4.
        tiles (str): The tiles to use for the map. Defaults to 'OpenStreetMap'.

    Returns:
        A Folium map object.
    """
    # Create a list of coordinates from the dataframe columns 'Start_Lat' and 'Start_Lng'
    heat_data = list(zip(df_loc.start_lat.values, df_loc.start_lng.values))

    # Create a map centered around the specified coordinates
    world_map = folium.Map(location=[latitude, longitude], zoom_start=zoom, tiles=tiles)

    # Add the heatmap layer to the map
    folium.plugins.HeatMap(heat_data, radius=12).add_to(world_map)

    return world_map

def conditions(condition, accidents_conditions=accidents_conditions):
    """
    This function takes in a condition as a string and returns a Pie chart showing
    the percentage of occurence of that condition in the data.

    Parameters:
        condition (str): The condition to generate the chart for.
        accidents_conditions (DataFrame): The dataframe containing the accidents data.
            Defaults to the global 'accidents_conditions' variable.
    Returns:
        A Plotly figure object.
    """
    condition_c = condition.replace(" ", "_").lower().strip()
    condition_data = accidents_conditions[condition_c].value_counts()
    fig = go.Figure(data=[go.Pie(values=condition_data.values, labels=condition_data.index, hole=.4)])
    fig.update_layout(
        title=dict(
            text=f"Percentage of {condition} occurance", xanchor='center', x=0.5
        ),
        xaxis_showgrid=False,
        yaxis_showgrid=False,
        showlegend=False,
        height=400,
        title_x=0.5,
        title_y=0.9
    )
    return fig
