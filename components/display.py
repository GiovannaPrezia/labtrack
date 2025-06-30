import streamlit as st
import pandas as pd
import base64
import json
from urllib.parse import quote
from pathlib import Path

# —————————————————————————————————————————————
# Função para carregar os demos iniciais (se existir arquivo JSON)
# —————————————————————————————————————————————
@st.cache_data
def carregar_protocolos_demo():
    demo_path = Path("demo_display/protocolos_demo.json")
    if demo_path.exists():
        return pd.DataFrame(json.loads(demo_path.read_text(encoding="utf-8")))
    return pd.DataFrame()

# —————————————————————————————————————————————
# Form de cadastro de protocolo
# —————————————————————————————————————————————
def form_cadastro():
    st.sidebar.header("➕ Cadastrar Protocolo Novo")
    with st.sidebar.form("form_cadastro"):
        nome     = st.text_input("Nome do Protocolo")
        grupo    = st.text_input("Grupo")
        categoria= st.text_input("Categoria")
        versao   = st.text_input("Versão")
        data     = st.date_input("Data")
        validade = st.date_input("Validade")
        autor    = st.text_input("Autor")
        email    = st.text_input("Email do Autor")
        depto    = st.text_input("Departamento")
        cargo    = st.text_input("Cargo")
        reagentes= st.text_input("Reagentes (vírgula-separated)")
        referencia_autor = st.text_input("Ref: Autor")
        referencia_ano   = st.text_input("Ref: Ano")
        referencia_doi   = st.text_input("Ref: DOI")
        referencia_link  = st.text_input("Ref: Link")
        # upload de PDF OU link externo
        pdf_file = st.file_uploader("Anexar PDF", type=["pdf"])
        pdf_link = st.text_input("Ou cole aqui um link externo para o PDF")

        ok = st.form_submit_button("💾 Salvar")
        if ok:
            # gera um ID simples
            novo_id = f"proto{len(st.session_state.dados)+1:03d}"
            # bytes do PDF
            arquivo_bytes = None
            if pdf_file is not None:
                arquivo_bytes = base64.b64encode(pdf_file.read()).decode()
            # decide qual link exibir
            arquivo_link = pdf_link if pdf_link else None

            novo = {
                "id": novo_id,
                "nome": nome,
                "grupo": grupo,
                "categoria": categoria,
                "versao": versao,
                "data": str(data),
                "validade": str(validade),
                "autor": autor,
                "email": email,
                "departamento": depto,
                "cargo": cargo,
                "reagentes": reagentes,
                "arquivo_nome": pdf_file.name if pdf_file else "",
                "arquivo_bytes": arquivo_bytes,
                "arquivo_link": arquivo_link,
                "historico": [],
                "referencia": {
                    "autor": referencia_autor,
                    "ano": referencia_ano,
                    "doi": referencia_doi,
                    "link": referencia_link
                },
                "comentarios": []
            }

            # adiciona ao DataFrame em memória
            st.session_state.dados = pd.concat([st.session_state.dados, pd.DataFrame([novo])], ignore_index=True)
            st.success(f"Protocolo '{nome}' cadastrado com sucesso!")

# —————————————————————————————————————————————
# Exibição dos protocolos (com PDF e link)
# —————————————————————————————————————————————
def exibir_protocolos():
    df = st.session_state.dados
    if df.empty:
        st.info("Nenhum protocolo cadastrado.")
        return

    st.title("🔬 LabTrack: Protocolos Cadastrados")
    termo = st.text_input("🔍 Buscar por nome")
    if termo:
        df = df[df["nome"].str.contains(termo, case=False, na=False)]

    for _, row in df.iterrows():
        with st.container():
            st.markdown(f"---\n### 📄 {row['nome']}  \n"
                        f"**Versão** {row['versao']} • **Data** {row['data']}")
            # — PDF embutido + download
            if pd.notna(row.get("arquivo_bytes")):
                pdf_bytes = base64.b64decode(row["arquivo_bytes"])
                # botão de download
                st.download_button(
                    "📥 Baixar PDF",
                    data=pdf_bytes,
                    file_name=row["arquivo_nome"],
                    mime="application/pdf"
                )
                # embed inline
                b64 = row["arquivo_bytes"]
                iframe = (
                    f'<iframe src="data:application/pdf;base64,{b64}" '
                    f'width="100%" height="500px" type="application/pdf"></iframe>'
                )
                st.components.v1.html(iframe, height=500)
            # — Link externo para PDF (Drive, etc.)
            elif pd.notna(row.get("arquivo_link")):
                st.markdown(f"[📂 Abrir PDF Externo]({row['arquivo_link']})")
            else:
                st.info("Nenhum PDF anexado nem link externo.")

            # demais metadados
            st.write(f"👤 **Autor**: {row['autor']} ({row['email']})")
            st.write(f"🏢 **Depto.**: {row['departamento']} | **Cargo**: {row['cargo']}")
            st.write(f"🧪 **Reagentes**: {row['reagentes']}")
            ref = row["referencia"]
            st.write(f"🔗 **Referência**: {ref['autor']}, {ref['ano']}, DOI {ref['doi']}, [Link]({ref['link']})")

# —————————————————————————————————————————————
# Main
# —————————————————————————————————————————————
if "dados" not in st.session_state:
    st.session_state.dados = carregar_protocolos_demo()

form_cadastro()
exibir_protocolos()
