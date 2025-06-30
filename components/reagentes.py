import streamlit as st
from urllib.parse import quote, unquote
import base64
import os
import json

def exibir_reagentes():
    st.header("🧪 Cadastro de Reagentes e Soluções")

    # Garantir que reagentes é um DataFrame
    if "reagentes" not in st.session_state or isinstance(st.session_state.reagentes, list):
        st.session_state.reagentes = pd.DataFrame(columns=[
            "nome", "componentes", "preparo", "validade", "responsavel", "local",
            "arquivo_nome", "arquivo_bytes"
        ])

    with st.form("cadastro_reagente_direto"):
        st.subheader("➕ Cadastrar Novo Reagente ou Solução")
        nome = st.text_input("Nome do Reagente/Solução")
        componentes = st.text_input("Composição / Componentes")
        validade = st.date_input("Validade")
        responsavel = st.text_input("Responsável")
        local = st.text_input("Local de Armazenamento")
        arquivo = st.file_uploader("📎 Protocolo de preparo (PDF opcional)", type=["pdf"], key="arquivo_reagente_manual")

        enviar = st.form_submit_button("💾 Salvar Reagente")
        if enviar and nome:
            novo = {
                "nome": nome.upper(),
                "componentes": componentes.upper(),
                "preparo": "",
                "validade": validade.strftime("%Y-%m-%d"),
                "responsavel": responsavel.upper(),
                "local": local.upper(),
                "arquivo_nome": arquivo.name if arquivo else None,
                "arquivo_bytes": arquivo.read() if arquivo else None
            }

            st.session_state.reagentes = pd.concat(
                [st.session_state.reagentes, pd.DataFrame([novo])],
                ignore_index=True
            )
            st.success("✅ Reagente cadastrado com sucesso!")

    st.subheader("📋 Lista de Reagentes Cadastrados")

    reagentes_df = pd.concat([
        st.session_state.get("reagentes", pd.DataFrame()),
        st.session_state.get("reagentes_demo", pd.DataFrame())  # opcional, se existir
    ], ignore_index=True)

    if reagentes_df.empty:
        st.info("Nenhum reagente cadastrado.")
    else:
        st.dataframe(reagentes_df)
