import streamlit as st

st.set_page_config(page_title='Test', page_icon='✈️')

create_page = st.Page("create.py", title="Create entry", icon=":material/add_circle:")
delete_page = st.Page("delete.py", title="Delete entry", icon=":material/delete:")
