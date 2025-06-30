import streamlit as st
from st_pages import add_page_title

# 1️⃣ Define <head>: title, favicon e layout wide
add_page_title(layout="wide")

# 3️⃣ Cabeçalho global — aparece acima do menu de pages
st.markdown("# 🔬 LabTrack")

# 4️⃣ Nada mais aqui: o st_pages faz todo o roteamento pelas .py em pages/
