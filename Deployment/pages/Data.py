import pandas as pd 
import streamlit as st 
from zipfile import ZipFile




zip_file_path = "./Deployment/source/US_Accidents_March23_analysis.zip"
with ZipFile(zip_file_path, 'r') as zip_ref:
    zip_ref.extractall()
extracted_files = zip_ref.namelist()
csv_file_name = extracted_files[0] 
data = pd.read_csv(csv_file_name)

st.markdown('''<center> <h1> US Accidents Data </h1> </center>''',unsafe_allow_html=True)
st.markdown('<a href ="https://www.kaggle.com/datasets/sobhanmoosavi/us-accidents/data"> <center> <h2> Link </h2> </center> ', unsafe_allow_html=True)
st.write(data)

st.markdown('''<center> <h1> Used data after cleaning and feature engineering</h1> </center>''',unsafe_allow_html=True)
zip_file_path = r"E:\Epsilon AI\MID PROJECT\Deployment\source\US_data_cleand.zip"
with ZipFile(zip_file_path, 'r') as zip_ref:
    zip_ref.extractall()
extracted_files = zip_ref.namelist()
csv_file_name = extracted_files[0] 
data_cleand = pd.read_csv(csv_file_name)
st.write(data_cleand)

st.markdown('''<center> <h1>Accident Conditions Data</h1> </center>''',unsafe_allow_html=True)
zip_file_path = r"E:\Epsilon AI\MID PROJECT\Deployment\Source\accidents_conditions.zip"
with ZipFile(zip_file_path, 'r') as zip_ref:
    zip_ref.extractall()
extracted_files = zip_ref.namelist()
csv_file_name = extracted_files[0] 
accidents_conditions = pd.read_csv(csv_file_name)
st.write(accidents_conditions)

