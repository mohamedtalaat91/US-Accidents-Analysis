
import streamlit as st

st.markdown('''<center> <h1> About </center>''', unsafe_allow_html=True)

st.markdown(
    """ <center> <h5>
    This web app is created using Streamlit.
               </center>""",unsafe_allow_html=True)

st.markdown(
    """<h4> <br> <br>
    Analysis about US accidents.
               </h4""",unsafe_allow_html=True)

st.markdown("""<h6>
    about data :
               </h6>""",unsafe_allow_html=True)

st.write("This data is a subset of large data containing the US accidents from 2016 to 2023.")      
st.write( "The original data contains about 7.7 Million records and 46 columns." )          
st.write("this subset data is splited randomly by sklearn library.")
st.write( "Ensurd the sample is random and gives the same results as the original data." )   
st.markdown("""<h6> <br>
    About  The Analysis Flow :
               </h6>""",unsafe_allow_html=True)  
st.write(" 1- Load the data ")
st.write( "2- explore the data") 
st.write(" 3- clean the data ")
st.write(" 4- make new features (features engineering)")    
st.write(" 5- perform EDA and gain insights")