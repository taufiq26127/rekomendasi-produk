import streamlit as st
from multiapp import MultiApp
from apps import papua_selatan

app = MultiApp()

# Add all your application here
st.title("Rekomendasi Produk")
app.add_app("Papua Selatan", papua_selatan.app)

# The main app
app.run()
