import numpy as np 
import pandas as pd
import streamlit as st


st.markdown("<h1 style='text-align: center;'>US Accidents Analysis</h1>", unsafe_allow_html=True)
st.markdown('''
<center> <h5>
            This project is for Analyzing US Accidents between 2016 and 2023.
            </center> </h5>''',unsafe_allow_html=True)


# st.markdown("![Alt Text](https://media1.giphy.com/media/v1.Y2lkPTc5MGI3NjExeTUwNmZhZ3Zqd2tua3J1bHgyaTg0NzByeWF0Mjl6azdzZmV1ZnlmaCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9cw/6EvCPYcf11rWNFPFWy/giphy.gif)", unsafe_allow_html=True)
# st.image("https://media1.giphy.com/media/v1.Y2lkPTc5MGI3NjExeTUwNmZhZ3Zqd2tua3J1bHgyaTg0NzByeWF0Mjl6azdzZmV1ZnlmaCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9cw/6EvCPYcf11rWNFPFWy/giphy.gif")

col1, col2, col3 = st.columns([1,2,1])
# Display the GIF in the middle column to center it
with col2:
    st.image("https://media1.giphy.com/media/v1.Y2lkPTc5MGI3NjExeTUwNmZhZ3Zqd2tua3J1bHgyaTg0NzByeWF0Mjl6azdzZmV1ZnlmaCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9cw/6EvCPYcf11rWNFPFWy/giphy.gif")
st.markdown('''
<center> <h10>
            Done by : Mohamed Talaat <br>
            Supervised by : Epsilon AI <br>
            
            ''',unsafe_allow_html=True)
