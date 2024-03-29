import streamlit as st
import numpy as np

st.title("RFR's Weather File Viewer")

#---/File uploader/---
file = st.file_uploader("Upload the wather file:", type = "epw",
                        accept_multiple_files = False)

#---/Read the data/---
if file:
    print(file)
