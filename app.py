import streamlit as st
import pandas as pd
import json
from components import forms, display, reagentes, export

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

# ——— Redirecionamento automático por URL ———
query_params = st.experimental_get_query_params()
menu_default = query_params.get("aba", ["📋 Cadastrar Novo Protocolo"])[0]

options = [
    "📋 Cadastrar Novo Protocolo",
    "📄 Protocolos Laboratoriais",
    "🧬 Lista de Reagentes",
    "📤 Exportar / Backups"
]
# define índice padrão, cai em 0 se não encontrar
default_idx = options.index(menu_default) if menu_default in options else 0

# Menu lateral
menu = st.sidebar.radio("Menu", options, index=default_idx)

# Navegação
if menu == options[0]:
    forms.exibir_formulario()
elif menu == options[1]:
    display.exibir_protocolos()
elif menu == options[2]:
    reagentes.exibir_reagentes()
elif menu == options[3]:
    export.exportar_dados()
