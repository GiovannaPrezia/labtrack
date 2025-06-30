import streamlit as st
from datetime import datetime
import uuid
import pandas as pd

def exibir_formulario():
    st.header("📋 Cadastrar Novo Protocolo")

    st.markdown("""
        <style>
        div[data-testid="stTextInput"] input,
        div[data-testid="stTextArea"] textarea {
            text-transform: uppercase;
        }
        </style>
    """, unsafe_allow_html=True)

    aba_protocolo, aba_reagente = st.tabs([
        "📑 CADASTRO DE PROTOCOLO",
        "🧪 CADASTRO DE REAGENTE/SOLUÇÃO"
    ])

    # Inicializa reagentes como DataFrame se necessário
    if "reagentes" not in st.session_state or isinstance(st.session_state.reagentes, list):
        st.session_state.reagentes = pd.DataFrame(columns=[
            "nome", "componentes", "preparo", "validade", "responsavel", "local",
            "arquivo_nome", "arquivo_bytes", "arquivo_link"
        ])

    # Inicializa dados de protocolos se ainda não existir
    if "dados" not in st.session_state or isinstance(st.session_state.dados, list):
        st.session_state.dados = pd.DataFrame(columns=[
            "id","nome","grupo","categoria","versao","data","validade",
            "autor","email","departamento","cargo","reagentes",
            "arquivo_nome","arquivo_bytes","arquivo_link",
            "historico","referencia","comentarios"
        ])

    with aba_protocolo:
        with st.form("form_protocolo"):
            nome        = st.text_input("Nome do Protocolo")
            grupo       = st.text_input("Grupo ou Área")
            categoria   = st.selectbox("Categoria do Protocolo", [
                "Extração de DNA", "Extração de RNA", "Cultivo Celular",
                "Transfecção", "Diferenciação Celular", "Outro"
            ])
            versao      = st.text_input("Versão", value="1.0")
            data        = st.date_input("Data de Criação", value=datetime.today())
            validade    = st.date_input("Validade do Protocolo")
            autor       = st.text_input("Nome do Autor")
            email       = st.text_input("E-mail")  # aqui não upper()
            departamento= st.text_input("Departamento")
            cargo       = st.text_input("Cargo")

            opcoes      = st.session_state.reagentes["nome"].tolist() if not st.session_state.reagentes.empty else []
            reagentes_usados = st.multiselect("Reagentes Utilizados", opcoes)

            st.markdown("### 📑 Protocolo (PDF ou Link)")
            st.info("Você pode **anexar um PDF** ou **colar um link externo** para visualização.")
            arquivo_protocolo = st.file_uploader(
                "Anexar arquivo PDF",
                type=["pdf"],
                key="arquivo_protocolo"
            )
            pdf_link = st.text_input("Ou cole aqui o link externo para o PDF", key="pdf_link")

            st.markdown("### 🔗 Referência do Protocolo")
            ref_autor = st.text_input("Autor da Referência")
            ref_ano   = st.text_input("Ano da Publicação")
            ref_doi   = st.text_input("DOI")
            ref_link  = st.text_input("Link HTML")

            st.markdown("### 📎 Anexos Adicionais")
            st.file_uploader(
                "Anexar outros arquivos (WORD, imagens, .csv etc.)",
                type=["pdf","png","jpg","jpeg","docx","txt","xlsx","csv"],
                key="anexos_adicionais_protocolo"
            )

            submitted = st.form_submit_button("💾 Salvar Protocolo")
            if submitted:
                novo_id = str(uuid.uuid4())[:8]

                # processa PDF anexado
                arquivo_bytes = None
                arquivo_nome  = None
                if arquivo_protocolo:
                    arquivo_bytes = arquivo_protocolo.read()
                    arquivo_nome  = arquivo_protocolo.name

                # usa link externo se fornecido
                arquivo_link = pdf_link.strip() or None

                novo = {
                    "id": novo_id,
                    "nome": nome.upper(),
                    "grupo": grupo.upper(),
                    "categoria": categoria.upper(),
                    "versao": versao.upper(),
                    "data": data.strftime("%Y-%m-%d"),
                    "validade": validade.strftime("%Y-%m-%d"),
                    "autor": autor.upper(),
                    "email": email,  # removido upper()
                    "departamento": departamento.upper(),
                    "cargo": cargo.upper(),
                    "reagentes": ", ".join(reagentes_usados),
                    "arquivo_nome": arquivo_nome,
                    "arquivo_bytes": arquivo_bytes,
                    "arquivo_link": arquivo_link,
                    "historico": [],
                    "referencia": {
                        "autor": ref_autor.upper(),
                        "ano": ref_ano.upper(),
                        "doi": ref_doi.upper(),
                        "link": ref_link
                    },
                    "comentarios": []
                }

                st.session_state.dados = pd.concat(
                    [st.session_state.dados, pd.DataFrame([novo])],
                    ignore_index=True
                )
                st.success("✅ Protocolo cadastrado com sucesso!")

    with aba_reagente:
        with st.form("form_reagente"):
            nome_sol    = st.text_input("Nome da Solução/Reagente")
            col1, col2, col3 = st.columns([2,2,2])
            with col1:
                comp      = st.text_input("Componente")
            with col2:
                conc      = st.text_input("Concentração")
            with col3:
                unidade   = st.selectbox("Unidade", ["%","mL","µL","mg/mL","g/L","OUTRO"])

            st.markdown("### 📑 Protocolo do Reagente (PDF ou Link)")
            st.info("Você pode **anexar um PDF** ou **colar um link externo**.")
            arquivo_reagente = st.file_uploader(
                "Anexar protocolo de preparo (PDF)",
                type=["pdf"],
                key="arquivo_reagente"
            )
            reag_link = st.text_input("Ou link externo para o protocolo do reagente", key="reag_link")

            validade_reag = st.date_input("Validade da Solução")
            responsavel   = st.text_input("Responsável pelo Preparo")
            local         = st.text_input("Armazenamento/Localização")

            st.markdown("### 📎 Anexos Adicionais")
            st.file_uploader(
                "Anexar outros arquivos (WORD, imagens, .csv etc.)",
                type=["pdf","png","jpg","jpeg","docx","txt","xlsx","csv"],
                key="anexos_adicionais_reagente"
            )

            enviar = st.form_submit_button("💾 Salvar Reagente/Solução")
            if enviar:
                bytes_reag = None
                nome_reag  = None
                if arquivo_reagente:
                    bytes_reag = arquivo_reagente.read()
                    nome_reag  = arquivo_reagente.name

                link_reag = reag_link.strip() or None

                novo_reagente = {
                    "nome": nome_sol.upper(),
                    "componentes": f"{comp.upper()} – {conc.upper()} {unidade}",
                    "preparo": "",
                    "validade": validade_reag.strftime("%Y-%m-%d"),
                    "responsavel": responsavel.upper(),
                    "local": local.upper(),
                    "arquivo_nome": nome_reag,
                    "arquivo_bytes": bytes_reag,
                    "arquivo_link": link_reag
                }

                st.session_state.reagentes = pd.concat(
                    [st.session_state.reagentes, pd.DataFrame([novo_reagente])],
                    ignore_index=True
                )
                st.success("✅ Reagente/Solução cadastrada!")
