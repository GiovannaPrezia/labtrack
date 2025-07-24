import streamlit as st
import pandas as pd
import json
from components import forms, display, reagentes, export, mapa

st.set_page_config(page_title="Controle de Protocolos", page_icon="🧪", layout="wide")

# Inicializar dados
if "dados" not in st.session_state:
    try:
        st.session_state.dados = pd.read_csv("data/protocolos.csv")
    except FileNotFoundError:
        with open("demo_display/protocolos_demo.json") as f:
            st.session_state.dados = pd.DataFrame(json.load(f))

if "reagentes" not in st.session_state:
    try:
        st.session_state.reagentes = pd.read_csv("data/reagentes.csv")
    except FileNotFoundError:
        with open("demo_display/reagentes_demo.json") as f:
            st.session_state.reagentes = pd.DataFrame(json.load(f))

# Menu lateral
menu = st.sidebar.radio("Menu", [
    "📋 Cadastrar Novo Protocolo",
    "🗺️ Mapa do Laboratório",
    "📄 Protocolos Laboratoriais",
    "🧬 Lista de Reagentes",
    "📤 Exportar / Backups"
])

# Navegação
if menu == "📋 Cadastrar Novo Protocolo":
    forms.exibir_formulario()
elif menu == "🗺️ Mapa do Laboratório":
    mapa.exibir_mapa()
elif menu == "📄 Protocolos Laboratoriais":
    display.exibir_protocolos()
elif menu == "🧬 Lista de Reagentes":
    reagentes.exibir_reagentes()
elif menu == "📤 Exportar / Backups":
    export.exportar_dados()
