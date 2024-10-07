import streamlit as st

st.set_page_config(page_title='Test', page_icon='✈️')

with st.sidebar:
    intro_button = st.button('Intro')
    flights_button = st.button('Vluchten')
    airports_button = st.button('Airports')
