import streamlit as st
import pandas as pd
import uuid
import datetime

def exibir_formulario():
    st.header("Cadastro de Novo Protocolo")

    with st.form("form_protocolo"):
        nome = st.text_input("Nome do Protocolo")
        grupo = st.text_input("Grupo Responsável")
        categoria = st.selectbox("Categoria", ["Extração", "Cultivo Celular", "PCR", "Western Blot", "Outros"])
        versao = st.text_input("Versão do Protocolo")
        data = st.date_input("Data de Criação", value=datetime.date.today())
        validade = st.date_input("Validade do Protocolo")
        autor = st.text_input("Nome do Autor")
        email = st.text_input("Email para Contato")
        departamento = st.text_input("Departamento")
        cargo = st.text_input("Cargo")
        reagentes = st.multiselect("Reagentes Utilizados", st.session_state.reagentes["nome"].tolist() if not st.session_state.reagentes.empty else [])
        
        arquivo = st.file_uploader("Anexar Protocolo (PDF ou Word)", type=["pdf", "docx"])
        
        # Referência
        st.subheader("Referência")
        ref_autor = st.text_input("Nome do Autor")
        ref_ano = st.text_input("Ano")
        ref_doi = st.text_input("DOI ou link")

        # Comentário
        st.subheader("Comentário (opcional)")
        comentario_nome = st.text_input("Seu nome")
        comentario_lab = st.text_input("Laboratório")
        comentario_texto = st.text_area("Comentário")

        submit = st.form_submit_button("Salvar Protocolo")

        if submit:
            novo = {
                "id": str(uuid.uuid4()),
                "nome": nome,
                "grupo": grupo,
                "categoria": categoria,
                "versao": versao,
                "data": str(data),
                "validade": str(validade),
                "autor": autor,
                "email": email,
                "departamento": departamento,
                "cargo": cargo,
                "reagentes": reagentes,
                "arquivo_nome": arquivo.name if arquivo else None,
                "arquivo_bytes": arquivo.getvalue() if arquivo else None,
                "referencia_autor": ref_autor,
                "referencia_ano": ref_ano,
                "referencia_doi": ref_doi,
                "comentario_nome": comentario_nome,
                "comentario_lab": comentario_lab,
                "comentario_texto": comentario_texto,
                "historico": [{"acao": "criado", "data": str(datetime.datetime.now())}]
            }
            st.session_state.dados = pd.concat([st.session_state.dados, pd.DataFrame([novo])], ignore_index=True)
            st.success("Protocolo cadastrado com sucesso!")
