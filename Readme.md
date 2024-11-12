

CDSP Deploma Mid Project

US Acceidents Data Analysis

  Project Overview

  US Accidents Analysis

    -   This data is a subset of large data containing the US accidents
        from 2016 to 2023.
    -   The original data contains about 7.7 Million records and 46
        columns.
    -   this subset data is splited randomly by sklearn library.
    -   Ensurd the sample is random and gives the same results as the
        original data.

  Flow of EDA

    1- Load the data
    2- explore the data
    3- clean the data
    4- make new features (features engineering)
    5- perform EDA and gain insights

    # import libraries
    import pandas as pd 
    import numpy as np
    import plotly.express as px
    import plotly.graph_objects as go
    from sklearn.impute import SimpleImputer
    import folium
    from folium.plugins import HeatMap
    from datasist.structdata import detect_outliers 
    from plotly.subplots import make_subplots
    from zipfile import ZipFile

    # read data
    zip_file_path = r"E:\Epsilon AI\MID PROJECT\Deployment\source\US_Accidents_March23_analysis.zip"
    with ZipFile(zip_file_path, 'r') as zip_ref:
        zip_ref.extractall()
    extracted_files = zip_ref.namelist()
    csv_file_name = extracted_files[0] 
    data = pd.read_csv(csv_file_name)

    data.info()

    data.shape

    # convert column names to lowercase
    data.columns= data.columns.str.lower()

    data.columns

droping some columns that are not needed

    data.drop(['id','source','description','street','airport_code','wind_direction','precipitation(in)','civil_twilight','nautical_twilight','astronomical_twilight','wind_chill(f)','pressure(in)','weather_timestamp','zipcode'],axis=1,inplace=True)

spliting data into 'data about accident' and 'accident conditions'

    accidents_conditions= data[['amenity','bump', 'crossing', 'give_way', 'junction', 'no_exit', 'railway','roundabout', 'station', 'stop', 'traffic_calming', 'traffic_signal','turning_loop']]

    data.drop(accidents_conditions.columns,axis=1,inplace=True)

chicking for missing values

    data.isna().sum()

    #percentage of missing values in each column
    missing_percentage = data.isna().sum().sort_values(ascending = False) / len(data) * 100
    px.bar(missing_percentage[missing_percentage > 0], color=missing_percentage[missing_percentage > 0], text_auto = True,color_continuous_scale=px.colors.sequential.Emrld)

    # conver to datetime
    data.start_time = pd.to_datetime(data.start_time,format='mixed')
    data.end_time = pd.to_datetime(data.end_time,format='mixed')

    # check for distance = 0
    data[round(data['distance(mi)'],1) == 0.0].shape

why we have few records with distance = 0

-   there is many accidents with no impact on the road and don't make a
    large disabled distance in the road
-   it's small accident , so the start and end coordinates are same
-   based on that we have a few missing values in end_lat , end_lng
    coulmns
-   so we will fill the missing values with start_lat , start_lng

    data['end_lat'].fillna(data['start_lat'], inplace=True)
    data['end_lng'].fillna(data['start_lng'], inplace=True)

    # convert to object
    data.start_lat = data.start_lat.astype(object)
    data.start_lng = data.start_lng.astype(object)
    data.end_lat = data.end_lat.astype(object)
    data.end_lng = data.end_lng.astype(object)

    data.info()

filling missing values

-   in the following columns we will fill the missing values with median
    because of outliers

    imputer = SimpleImputer(missing_values=np.nan, strategy='median')
    data[['humidity(%)','visibility(mi)','wind_speed(mph)','temperature(f)']] = imputer.fit_transform(data[['humidity(%)','visibility(mi)','wind_speed(mph)','temperature(f)']])

detecting outliers and removing it

    idx = detect_outliers(data, 0,['temperature(f)','wind_speed(mph)'])
    data.drop(idx , inplace=True)

    idx = data[(data['visibility(mi)']<0) | (data['visibility(mi)']>50)].index
    data.drop(idx,inplace= True)

filling timezone missing values

-   sorting data by the longtude which is the time zone is sorted by
-   starting from the lowest (US_Pacific) to the highest (US_Estern)

    data.timezone.unique()

    data.sort_values(by= 'start_lng',inplace=True)
    data.timezone.ffill(inplace=True)

filling missing values with ffill
we will fill the missing values with ffill because this is a time series
data and we need to fill the missing values with the previous value
it's logicaly more accurate

    data.sort_values(by='start_time',inplace=True)
    data.sunrise_sunset.ffill(inplace=True)
    data.weather_condition.ffill(inplace = True)

dropping duplicates and null values

    data.dropna(inplace=True)

    data.drop_duplicates(inplace=True)

    data.shape

    data.reset_index(drop=True, inplace=True)

    data.head(5)

feature engineering

adding new date and time features

    data['year'] = data['start_time'].dt.year
    data['month_name'] = data['start_time'].dt.month_name()
    data['day_name'] = data['start_time'].dt.day_name()
    data['hour'] = data['start_time'].dt.hour
    data['duration'] = data['end_time']-data['start_time']

    px.box(data, x=data['duration'].dt.days)

dropping outliers in duration the detect outliers function returns a
huge amount of outliers in the duration column that will affect the
analysis
we will leave the accidents with duration less than 2 days
the data with 1 day is containing 1 day and up to 23 hours and 59
minutes
converting it to hours

    idx = data[data.duration.dt.days >1].index
    data.drop(idx , inplace=True)

    data.duration = data.duration.dt.total_seconds() / 3600

get season from month name

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

getiing the distance

-   there is two ways to git the distance by kilometers
-   one is using the geopy library 'takes a lot of time and not accurate
    with the small distances'
-   another is using the conversion formula

    # from geopy.distance import great_circle
    # def get_dist(x):
    #     loc_1 = (x['start_lat'], x['start_lng'])
    #     loc_2 = (x['end_lat'], x['end_lng'])
    #     return great_circle(loc_1, loc_2).kilometers

    # # apply the fn to df and create new column for distance
    # data['distance(km)'] = data.apply(get_dist, axis=1)
    # data.head()

-   converting coulumns metrics

    data['distance(km)'] = data['distance(mi)']*1.60934
    data.drop(['distance(mi)'],axis=1,inplace=True)

    data['temperature(c)']= (data['temperature(f)']-32)*5/9
    data.drop(['temperature(f)'],axis=1,inplace=True)

    data['visibility(km)'] = data['visibility(mi)']*1.60934
    data.drop(['visibility(mi)'],axis=1,inplace=True)

    data['wind_speed(kmh)'] = data['wind_speed(mph)']*1.60934
    data.drop(['wind_speed(mph)'],axis=1,inplace=True)

weather condition
the weather condition is a categorical column that has a lot of values
that will affect the analysis
we will categorize the weather condition into 7 categories: 'Rain'
'Cloudy' 'Snow' 'Clear' 'Fog/Mist/Haze' 'Storm' 'Other'

    data.weather_condition.unique()

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

    data.weather_condition.unique()

ordering the columns

    columns_order = ['severity', 'start_time', 'end_time','duration','hour',
           'day_name', 'month_name', 'year' ,'season', 'start_lat', 'start_lng', 'end_lat', 'end_lng','timezone','distance(km)', 'city','county','state','country', 'temperature(c)','humidity(%)', 'visibility(km)', 'wind_speed(kmh)', 'weather_condition', 'sunrise_sunset']
    data = data.reindex(columns=columns_order)

    data.head()

The used color scheme
px.colors.sequential.Emrld_r

SEVERITY Analysis

-   the most frequent severity is level '2'
-   the sevirity levels is sorted by lowest to highest 1:4

    fig =px.bar(data, x=data.severity.value_counts().index, y=data.severity.value_counts().values,
             title="severity frequency",color_discrete_sequence=px.colors.sequential.Emrld_r)
    fig.update_layout(xaxis_title="Severity",yaxis_title="Frequency",title_x=0.5)

    severity_df = pd.DataFrame(data['severity'].value_counts()).rename(columns={'index':'Severity', 'count':'Cases'})
    fig = go.Figure(go.Funnelarea(
        text = ["Severity - 2","Severity - 3", "Severity - 4", "Severity - 1"],
        values = severity_df.Cases,title= "the impact of accedint on the road"))

    fig.show()

    fig = px.scatter(data,x= 'start_lng',y='start_lat',color= 'severity',color_continuous_scale=px.colors.sequential.Hot,hover_name='city')
    fig.update_layout(title_text="Accidents distribution in the US",title_x=0.5, width=800, height=600)

TIME ANALYSIS

2023 year not really expresses the number of accedints in 2023 'its only
to march'
1-In which year the most accidents happend in US?
2- which month have the most number of accidents and why?
3- how could the season affect the numbers of accedints ?
4 -what day have the most number of accidents?
5- what is the rush hours with accidents?
6- how could the Day - Night affect the numbers of accedints

we will answer this question with this visualisation

    data.info()

    cols = ['year', 'month_name',  'season','day_name', 'hour', 'sunrise_sunset']
    for col in cols :
        fig = px.bar(data, x=data[col].value_counts().index, y=data[col].value_counts().values,
                 title=col+" frequency",color = data[col].value_counts().values,text_auto = True ,color_continuous_scale=px.colors.sequential.Emrld)
        fig.update_layout(xaxis_title=col,yaxis_title="Frequency",title_x=0.5)
        fig.show()

    duration = data[data.duration < 10]
    px.histogram(duration,duration.duration,nbins = 10,color_discrete_sequence=px.colors.sequential.Emrld_r)

insights

-   2022 is the year with most number of accidents with 22.65% of all
    accidents

-   December is the peak month with 25.48 % of the accidents ; its most
    likely to be because DEC is rainy and snow month and the roads most
    time is wet which affect the driving control

-   Winter and autumn is seasons with Weather fluctuations and has a
    huge impact on the accidents ocurrance both of them got a 28.5% ,
    27.44% of the accidents

-   most days have likly percentages put suterday and sunday is the
    lowest among them because its weekend and most of people is satying
    home in weekend

-   hours with most accedints is the typical start and end time of work
    "the ruch hours" 7 and 8 is the peak in the morning and 4 and 5 is
    the peak in the evening

-   the most accedints is made in the day light and its likely because
    the work hours

-   most accidents impact is under the 1 hour duration

WEATHER ANALYSIS

    px.histogram(data,'temperature(c)',nbins=10, marginal = 'box',text_auto = True,color_discrete_sequence=px.colors.sequential.Emrld_r)

IN the Temperature range of (10 to 30) 67.47% of the road accidents
occurred

    px.histogram(data,'humidity(%)',nbins=10, marginal = 'box',text_auto = True,color_discrete_sequence=px.colors.sequential.Emrld_r)

IN the Humidity range of (60 to 70) 15.96 of the road accidents occurred
For around 45.42% of road accident cases , the humidity range is between
(60 to 90)

    px.histogram(data,'visibility(km)',nbins=10, marginal = 'box',text_auto = True,color_discrete_sequence=px.colors.sequential.Emrld_r)

In Maximun cases (81.34%) of road accidents , the Visivility range is
between 15 km to 25 km


    px.histogram(data,'wind_speed(kmh)',nbins=10, marginal = 'box',text_auto = True,color_discrete_sequence=px.colors.sequential.Emrld_r)

In the most cases around 40% of the accidents occurred while wind speed
is between 7.5 kmh and 12.5 kmh

    weather = data.groupby('weather_condition').size().nlargest(10) / len(data) * 100
    px.bar(weather,x=weather.index,y=weather.values,text_auto=True,title = 'percentage of weather condition occurance',color_discrete_sequence=px.colors.sequential.Emrld_r)

in total accident cases 45.7 % happend in clear weather

    px.box(data,x='weather_condition',y='temperature(c)' ,color= 'weather_condition',color_discrete_sequence=px.colors.sequential.Emrld_r)

the temperature distribution over each weather condition

    px.imshow(data.corr(numeric_only=True),color_continuous_scale=px.colors.sequential.Emrld_r)

there is no coorelation between the numerical columns

    data.describe().round(2)

LOCATION ANALYSIS

    # top 10 city percentages from accidents
    top_citys_percentage = data.groupby('city').size().nlargest(10) / len(data) * 100

    # plot the top 10 city percentages
    px.bar(top_citys_percentage, x=top_citys_percentage.index, y=top_citys_percentage.values,text_auto= True,
           title="Top 10 city percentages from accidents",color_discrete_sequence=px.colors.sequential.Emrld_r)

-   insights:

1.  Miami is the city with highest (2.43%) no. of road accidents in US
    (2016-2023).
2.  Houston is the city with 2nd highest (2.19%) no. of road accidents
    in US (2016-2023).
3.  Around 16.6% accident records of past 8 years are only from these 10
    cities out of 8884 cities in US

    # top 10 state percentages from accidents
    top_states_percentage = data.groupby('state').size().nlargest(10) / len(data) * 100

    # plot the top 10 state percentages
    px.bar(top_states_percentage, x=top_states_percentage.index, y=top_states_percentage.values,text_auto= True,
           title="Top 10 state percentages from accidents",color_discrete_sequence=px.colors.sequential.Emrld_r)

-   insights:

1.  in US , California is the state with the highest no of road
    accidents
2.  About 22.9% of the total accident record in US is only form
    California
3.  Florida is the 2nd highest (11.48% cases) state for no. road
    accidents in US.

    # top 10 state percentages from accidents
    top_states_percentage = data.groupby('state').size().nsmallest(10) / len(data) * 100

    # plot the top 10 state percentages
    px.bar(top_states_percentage, x=top_states_percentage.index, y=top_states_percentage.values,text_auto= True,
           title="Top 10 state percentages from accidents",color_discrete_sequence=px.colors.sequential.Emrld_r)

-   insights:

1.  South Dakota is the city with lowest no. of road accidents.
2.  only 1800 accidents took place in South Dakota

    # top 10 county percentages from accidents
    top_countys_percentage = data.groupby('county').size().nlargest(10) / len(data) * 100

    # plot the top 10 county percentages
    px.bar(top_countys_percentage, x=top_countys_percentage.index, y=top_countys_percentage.values,text_auto= True,
           title="Top 10 county percentages from accidents",color_discrete_sequence=px.colors.sequential.Emrld_r)

INSIGHTS

-   LOS ANGELES is the county with the highest no. of road accidents
    (7.1%) of total accidents in US
-   MIAMI-DADE is the county with the 2nd highest no. of road accidents
    in US
-   About 26 % of the total accident record in US is only form the TOP
    10 counties


    timezone = data.groupby('timezone').size().sort_values(ascending=False) / len(data) * 100
    px.bar(timezone, x=timezone.index, y=timezone.values,text_auto= True,
           title="Percentage of Accidents per Timezone",color_discrete_sequence=px.colors.sequential.Emrld_r)

-   INSIGHTS

1.  Eastern time zone reagion of US has the highest no. of road accident
    cases (46.78%)
2.  Mountain time zone reagion of US has the lowest no. of road accident
    cases (5.5%)

    fig = px.scatter(data,x= 'start_lng',y='start_lat',color= 'timezone',color_discrete_sequence=px.colors.sequential.solar,hover_name='city')
    fig.update_layout(title_text="Accidents distribution in each time zone",title_x=0.5, width=800, height=600)

ACCIDENTS CONDITIONS ANALYSIS

-   Identifying each accident condition percentages and what is the
    majority in each condition

    accidents_conditions.head(10)

    accidents_conditions.columns

INSIGHTS

    px.pie(accidents_conditions, names = accidents_conditions.bump.value_counts().index ,values =accidents_conditions.bump.value_counts().values.tolist() ,title = 'prescene of Bumper',hole = 0.5, color_discrete_sequence=px.colors.sequential.Emrld_r)

-   Almost in every case (99.95%) of the road accidents Bumper was
    absent in accident spot

    px.pie(accidents_conditions, names = accidents_conditions.crossing.value_counts().index ,values =accidents_conditions.crossing.value_counts().values.tolist() ,title = 'prescene of crossing',hole = 0.5, color_discrete_sequence=px.colors.sequential.Emrld_r)

-   In 5.7% cases, road accidents happened near the crossing.

    px.pie(accidents_conditions, names = accidents_conditions.give_way.value_counts().index ,values =accidents_conditions.give_way.value_counts().values.tolist() ,title = 'prescene of Give Way',hole = 0.5, color_discrete_sequence=px.colors.sequential.Emrld_r)

-   only a 0.5% of the road accidents happened while giving way.

    px.pie(accidents_conditions, names = accidents_conditions.junction.value_counts().index ,values =accidents_conditions.junction.value_counts().values.tolist() ,title = 'prescene of junction',hole = 0.5, color_discrete_sequence=px.colors.sequential.Emrld_r)

-   In 7.45% cases, road accidents happened near the junction , cross
    road.

    px.pie(accidents_conditions, names = accidents_conditions.stop.value_counts().index ,values =accidents_conditions.stop.value_counts().values.tolist() ,title = 'prescene of stop',hole = 0.5, color_discrete_sequence=px.colors.sequential.Emrld_r)

-   In 2.82% cases, road accidents happened while near or the stop area.

    px.pie(accidents_conditions, names = accidents_conditions.traffic_signal.value_counts().index ,values =accidents_conditions.traffic_signal.value_counts().values.tolist() ,title = 'prescene of Traffic Signal',hole = 0.5, color_discrete_sequence=px.colors.sequential.Emrld_r)

-   around 15% of the road accidents happened while near or in the
    traffic signal.

    px.pie(accidents_conditions, names = accidents_conditions.turning_loop.value_counts().index ,values =accidents_conditions.turning_loop.value_counts().values.tolist() ,title = 'prescene of Turning Loop',hole = 0.5, color_discrete_sequence=px.colors.sequential.Emrld_r)

-   there is no accidents happend while Turning Loop

    !pipreqs ./

End Of Analysis
