import streamlit as st
import os
from PIL import Image
st.set_page_config(
    page_title="Hello",
    page_icon="👋",
)

st.title("Catan Statistics App")

image = Image.open(os.path.abspath(os.path.join("catan-background.jpeg")))
st.image(image)



