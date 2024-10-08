import streamlit as st
from streamlit_option_menu import option_menu

st.set_page_config(page_title='Case 3 Vluchten (groep 3)', page_icon='✈️')

# sidebar
with st.sidebar: 
  selected = option_menu(menu_title="Menu", options=["Intro", "Vluchten", "Luchthavens"])

