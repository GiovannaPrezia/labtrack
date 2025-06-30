import streamlit as st
import pandas as pd

def exibir_reagentes():
    st.header("Cadastro de Reagentes ou Soluções")

    with st.form("form_reagente"):
        nome = st.text_input("Nome do Reagente")
        tipo = st.selectbox("Tipo", ["Solução", "Reagente", "Buffer", "Outro"])
        localizacao = st.text_input("Guardado em / Localização")

        submit = st.form_submit_button("Salvar Reagente")

        if submit and nome:
            novo = {"nome": nome, "tipo": tipo, "localizacao": localizacao}
            st.session_state.reagentes = pd.concat(
                [st.session_state.reagentes, pd.DataFrame([novo])],
                ignore_index=True
            )
            st.success("Reagente cadastrado com sucesso!")

    st.subheader("Reagentes Cadastrados")
    if st.session_state.reagentes.empty:
        st.info("Nenhum reagente cadastrado.")
    else:
        st.dataframe(st.session_state.reagentes)
