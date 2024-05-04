from streamlit_folium import folium_static
import streamlit as st
import sys 
sys.path.append("Deployment")
import MEDA as md



st.markdown("<h1 style='text-align: center;'>US Accidents Analysis Page</h1>", unsafe_allow_html=True)
# st.markdown("<h4>- Sequence of Analysis</h4>", unsafe_allow_html=True)
# st.markdown("<h6>1. SEVERITY ANALYSIS <br> <br> 2. TIME ANALYSIS <br> <br> 3. WEATHER ANALYSIS <br> <br> 4. LOCATION ANALYSIS   <br> <br> 5. ACCIDENTS CONDITIONS ANALYSIS</h6>", unsafe_allow_html=True)
tap1 , tap2 , tap3 , tap4 , tap5 = st.tabs(["SEVERITY ANALYSIS","TIME ANALYSIS","WEATHER ANALYSIS","LOCATION ANALYSIS","ACCIDENTS CONDITIONS ANALYSIS"])

with tap1:
    st.markdown("<h3>1. SEVERITY ANALYSIS</h3>", unsafe_allow_html=True)
    st.markdown("<h6>1.1.  ABOUT SEVERITY</h6>", unsafe_allow_html=True)
    st.write("The severity of an accident is a measure of the impact the accident caused to the traffic.")
    st.write("The severity is measured from low to high with 1 being the least severe and 4 being the most severe.")
    st.markdown("<h6>1.2. SEVERITY PERCENTAGES</h6>", unsafe_allow_html=True)
    st.write("most of the accidents have severity measured as \"2\"  with percentage of \"79.7%\"")
    st.plotly_chart(md.show_severity())

    st.markdown("<h6>1.3. SEVERITY DISTRIBUTION MAP Over the US country</h6>", unsafe_allow_html=True)
    st.write("This map shows the severity of accidents distributed over the country with ability to which severity value to show on the map.")
    severity = st.multiselect("Choose severity",(1,2,3,4),default=[1,2,3,4], key="severity")
    st.plotly_chart(md.severity_map(severity))



with tap2:
    st.markdown("<h3>2. TIME ANALYSIS</h3>", unsafe_allow_html=True)
    st.markdown("<h5>2.1.  ABOUT TIME</h5>", unsafe_allow_html=True)
    st.write("       The  start time of an accident is a measure of when the accident occurred.")
    st.write("       And the end time of an accident is a measure of when the accident Impact ended.")
    st.write("       All accidents in the data occurred between January 2016 and March 2023.")
    st.write("       The time of an accident is measured in 24 hour format.")
    st.write("       The Data is cleaned and Time outliers are removed, the maximum Duration of an accident is 48 hours.")




    st.markdown("<h5> <br> <br> 2.2. TIME ElEMENTS</h5>", unsafe_allow_html=True)
    st.write("Analyzing each time element and what is the impact of time on the accidents.")
    st.write("knowing  the trends of Time and when will the accidents increase or decrease is very important to manage  the Traffic and make a strong traffic management plan in order to reduce the number of accidents.")
    st.write("*note : The Data in 2023 is not complete (only the first 3 months of 2023)")
    category =st.radio("CHOOSE TIME PARAMETER",("Year","Month Name","Day Name","Hour","Season","Sunrise OR Sunset"), key="time",horizontal=True)
    st.plotly_chart(md.time_analysis(category))
   
    st.markdown("<h5> <br> <br> 2.3. Customized Time series Analysis</h5>", unsafe_allow_html=True)
    st.write("Analyzing each time element and its unique values and what is the difference between accidents distribution over each time element.")
    st.write("its important to see what is the Impact of time over the accidents not on the hole data , you can also specify multiple values of time like a day or month of year or multiple values of them.")
    st.write("so if you want to analyze the accidents only in summer or in CORONAVIRUS period you can choose it.")

    category =st.radio("Choose Time parameter",('Year',"Month Name","Day Name","Hour","Season","Sunrise OR Sunset"), key="time series",horizontal=True)
    time_value = st.multiselect(label="Select multiple values",options=md.time_selector(category),default=md.time_selector(category),key="time value")

    col1, col2 = st.columns(2,gap="large")
    with col1:
        st.plotly_chart(md.time_series(category,time_value,fig_num =1))
        st.plotly_chart(md.time_series(category,time_value,fig_num =2))
        st.plotly_chart(md.time_series(category,time_value,fig_num =6)) 

    with col2:
        st.plotly_chart(md.time_series(category,time_value,fig_num =3))
        st.plotly_chart(md.time_series(category,time_value,fig_num =4))
        st.plotly_chart(md.time_series(category,time_value,fig_num =5))
    st.markdown("<h5> <br> <br> 2.4. INSIGHTS</h5>", unsafe_allow_html=True)
    st.write("The main Insights from the time series analysis are the following :")
    st.write("1. 2022 is the year with most number of accidents with 22.76% of all accidents.")
    st.write("2. December is the peak month with 10.78 % of the accidents ; its most likely to be because DEC is rainy and snow month and the roads most time is wet which affect the driving control.")
    st.write("3. Winter and autumn is seasons with \"Weather fluctuations\" and has a huge impact on the accidents occurrence both of them got a 28.59% , 27.40% of the accidents ")
    st.write("4. most days have likely percentages put Saturday and Sunday is the lowest among them because its weekend and most of people is staying home in weekend ")
    st.write("5. hours with most accidents  is the typical start and end time of work \"the rush hours\" 7 and 8 is the peak in the morning and 4 and 5 is the peak in the evening ")
    st.write("6. the most accidents is made in the day light and its likely because the work hours ")
    st.write("7. most accidents impact is under the 1 hour duration ")

with tap3:
    st.markdown("<h3>3. WEATHER ANALYSIS</h3>", unsafe_allow_html=True)


    st.markdown("<h5>3.1.  ABOUT WEATHER</h5>", unsafe_allow_html=True)
    st.write(" The weather is an important factor in determining the severity of an accident and its impact on the traffic.")
    st.write (" There is strong relation between weather and the number of accidents that occurs.")
    st.write(" To know wat is the weather condition there is more than one factor : \" Temperature , Humidity , Wind Speed and Visibility\"")
    st.write(" Each factor can be a cause of an accident ")
    st.write(" Analyzing each weather condition can be very useful in traffic management plans considering that the weather is predictable.")


    st.markdown("<h5> <br> <br> 3.2. WEATHER ELEMENTS ANALYSIS</h5>", unsafe_allow_html=True)
    weather_category = st.radio("Choose weather",('Temperature(c)','Humidity(%)','Wind Speed(kmh)','Visibility(km)'), key="weather",horizontal=True)
    st.plotly_chart(md.weather_analysis(weather_category))
    st.markdown("<h5> <br> <br>  INSIGHTS</h5>", unsafe_allow_html=True)
    st.write("The main Insights from the WEATHER ANALYSIS are the following :")
    st.write("1. IN the Temperature range of (10 to 30) 67.47% of the road accidents occurred")
    st.write("2. IN the Humidity range of (60 to 70) 15.96% of the road accidents occurred , For around 45.42% of road accident cases , the Humidity range is between (60 to 90)")
    st.write("3. IN Maximum cases (81.34%) of road accidents , the Visibility range is between 15 km to 25 km.")
    st.write("4. IN the most cases around 40% of the accidents occurred while wind speed is between 7.5 kmh and 12.5 kmh.")
    st.write("5. the weather is predictable and it is one of the most effective factor in the accidents.")
    



    st.markdown("<h5> <br> <br>3.3. WEATHER DISTRIBUTION ANALYSIS</h3>", unsafe_allow_html=True)
    weather_category = st.radio("Choose weather",('Temperature(c)','Humidity(%)','Wind Speed(kmh)','Visibility(km)'), key="distribution",horizontal=True)
    st.plotly_chart(md.weather_distribution(weather_category))
    st.markdown("<h5> <br> <br> INSIGHTS</h5>", unsafe_allow_html=True)
    st.write("The main Insights from the WEATHER DISTRIBUTION ANALYSIS are the following :")
    st.write("1. Certain weather conditions are more likely to lead to accidents. This includes low visibility (fog, mist, haze), specific temperature ranges (around 0°C and 10°C, but the exact relationship might depend on other factors), and certain wind speeds (peaks at 20 and 30 km/h).")
    st.write("2. The impact of each weather condition might be interrelated. For instance, low visibility often occurs with fog or mist, which might explain the peak in accidents at those temperatures.")
    st.write("3. Humidity seems to have an inverse relationship with accidents.")
    



    st.markdown("<h5> <br> <br>3.4. WEATHER CONDITION OCCURENCE</h3>", unsafe_allow_html=True)
    st.write("Here you can specify the Year you want to analyze or analyze all the years:")
    time_value = st.multiselect(label="Select Years to analyze",options=[2023,2022, 2021, 2020, 2019, 2018, 2017, 2016],default=[2023,2022, 2021, 2020, 2019, 2018, 2017, 2016],key="weather time")
    st.plotly_chart(md.weather_occurance_per_year(time_value))
    st.markdown("<h5> <br> <br> INSIGHTS</h5>", unsafe_allow_html=True)
    st.write("The main Insights from the WEATHER CONDITION OCCURENCE are the following :")
    st.write("Clear skies are the most common weather condition. The chart shows that clear skies account for almost half (45.77%) of all weather conditions")
    st.write("Cloudy and rainy conditions are also relatively common. Cloudy skies make up 41.67% of all conditions, while rain accounts for 6.99%.")
    st.write("Overall, good visibility is the most common weather condition, with clear skies being the most frequent.  Cloudy conditions are also fairly common, but other conditions such as rain, fog, mist, haze, snow, and storms are less frequent")

with tap4:

    st.markdown("<h3> 4. LOCATION ANALYSIS </h3>", unsafe_allow_html=True)

    st.markdown("<h5> <br> <br> 4.1.  ABOUT LOCATION</h5>", unsafe_allow_html=True)
    st.write("The location of an accident is where the accident occurred in country")
    st.write("IN this data there is more than one indicator of location. The data includes :")
    st.write("City,State,County,Country,Longitude,Latitude")
    st.write("We will use thes parameters to analyze and show the places that have a high number of road accidents.")
    st.write("This can help in holding the Traffic in order to reduce the number of accidents.")

    st.markdown("<h5> <br> <br> 4.2.  HEAT MAP </h5>", unsafe_allow_html=True)
    st.write("This is a heat map that shows the distribution of road accidents.")
    # Create a heatmap for the entire US using the create_heatmap function
    map_us_heatmap = md.create_heatmap()
    folium_static(map_us_heatmap)

    st.markdown("<h5> <br> <br> 4.3.  LOCATION ELEMENTS ANALYSIS</h5>", unsafe_allow_html=True)
    st.write("this is an interactive chart that shows the percentage of accidents in each location with the ability to choose the number of locations to show on the chart.")
    st.write("note : The Smallest number of locations is a count not a percentage(the percentage is very small).")
    col1, col2 = st.columns(2,gap="large")
    with col1:
        location = st.radio("Choose location",('City','State','County'), key="elements",horizontal=True)
    with col2:
        sorting = st.radio("Choose sorting",('Largest','Smallest'), key="elements sorting",horizontal=True)
    num = st.number_input("Enter the number of locations to show",min_value=1, max_value=50, value=10,step=1)
    st.plotly_chart(md.location_analysis(location,num,sorting))
    st.markdown("<h5> <br> <br>  INSIGHTS</h5>", unsafe_allow_html=True)
    st.write("The main Insights from the LOCATION ANALYSIS are the following :")
    st.markdown("<h7>  LARGEST INSIGHTS</h7>", unsafe_allow_html=True)
    st.write("     1. Miami is the city with highest (2.44%) no. of road accidents in US (2016-2023).")
    st.write("  2. Los Angeles is the city with 2nd highest (2.20%) no. of road accidents in US (2016-2023).")
    st.write("  3. Around 16.6% accident records of past 8 years are only from these 10 cities out of 8884 cities in US")
    st.write("  4. in US , California is the state with the highest no of road accidents")
    st.write("  5. About 23% of the total accident record in US is only form California")
    st.write("  6. Florida is the 2nd highest (11.46% cases) state for no. road accidents in US.")
    st.write("   7. LOS ANGELES is the county with the highest no. of road accidents (7.18%) of total accidents in US")
    st.write("  8. MIAMI-DADE is the county with the 2nd highest no. of road accidents  in US")
    st.write("  9. About 26 % of the total accident record in US is only form the TOP 10 counties")
    st.markdown("<h7>  SMALLEST INSIGHTS</h7>", unsafe_allow_html=True)
    st.write("  1.South Dakota is the city with lowest no. of road accidents.")
    st.write("  2. only 8 accidents took place in South Dakota")
    st.write("  3. There is a big number of cities that occurred only one time (192) city")
    st.write("  4. \"252\" counties have only one accident occurred")


    st.markdown("<h5> <br> <br> TIME ZONE ANALYSIS </h5>",unsafe_allow_html=True)
    
    st.plotly_chart(md.time_zone())
    st.markdown("<h5> INSIGHTS </h5>",unsafe_allow_html=True)
    st.write("1. Eastern time zone region of US has the highest no. of road accident cases (46.78%)")
    st.write("2. Mountain time zone region of US has the lowest no. of road accident cases (5.5%)")

    st.markdown("<h5> <br> <br> TIME ZONE MAP </h5>",unsafe_allow_html=True)
    st.write("This map shows the distribution of road accidents in the time zone of the US")
    st.plotly_chart(md.time_zone_map())

with tap5:
    st.markdown("<h3>5. ACCIDENTS CONDITIONS ANALYSIS</h3>", unsafe_allow_html=True)
    st.markdown("<h5>5.1.  ABOUT CONDITIONS</h5>", unsafe_allow_html=True)
    st.write("       The conditions of an accident is a measure of the severity of the accident.")
    condition = st.radio("Choose condition",('Amenity', 'Bump', 'Crossing', 'Give Way', 'Junction', 'No Exit','Railway', 'Roundabout', 'Station', 'Stop', 'Traffic Calming','Traffic Signal', 'Turning Loop'), key="accident condition",horizontal=True)
    st.plotly_chart(md.conditions(condition))





   






