import streamlit as st
import pandas as pd
from urllib.parse import quote
from datetime import datetime
from pathlib import Path
import json

def carregar_protocolos_demo():
    try:
        demo_path = Path("demo_display/protocolos_demo.json")
        with demo_path.open("r", encoding="utf-8") as f:
            return pd.DataFrame(json.load(f))
    except Exception as e:
        st.warning(f"Erro ao carregar protocolos demo: {e}")
        return pd.DataFrame()

def exibir_protocolos():
    # Carregamento de dados demo, se necessário
    if "dados" not in st.session_state or st.session_state.dados.empty:
        st.session_state.dados = carregar_protocolos_demo()

    df = st.session_state.dados
    if df.empty:
        st.info("Nenhum protocolo cadastrado ainda.")
        return

    # Excluir protocolos de reagentes (caso esteja usando mesma tabela)
    df = df[df["categoria"] != "🧪 Protocolo de Reagentes/Soluções"]

    st.title("🔬 LabTrack: Plataforma de Controle de Versionamento de Protocolos")
    st.markdown("## Protocolos Cadastrados")

    termo = st.text_input("🔍 Buscar por nome do protocolo")
    if termo:
        df = df[df["nome"].str.contains(termo, case=False, na=False)]

    col_main, col_side = st.columns([4, 1.5])

    with col_main:
        for grupo in df["grupo"].dropna().unique():
            st.markdown(f"### 🧬 {grupo}")
            grupo_df = df[df["grupo"] == grupo]

            for categoria in grupo_df["categoria"].dropna().unique():
                st.markdown(f"#### 📁 {categoria}")
                cat_df = grupo_df[grupo_df["categoria"] == categoria]

                for _, row in cat_df.iterrows():
                    expand_key = f"detalhes_{row['id']}"
                    if expand_key not in st.session_state:
                        st.session_state[expand_key] = False

                    with st.container():
                        st.markdown(f"""
                            <div style='border:1px solid #444; border-radius:10px; 
                                        padding:10px; margin-bottom:10px; background-color:#111;'>
                                <strong>📄 {row['nome']}</strong><br>
                                <span style='font-size:13px;'>Versão {row['versao']} • {row['data']}</span><br>
                            </div>
                        """, unsafe_allow_html=True)

                        if st.button("🔍 Ver Detalhes", key=row["id"]):
                            st.session_state[expand_key] = not st.session_state[expand_key]

                        if st.session_state[expand_key]:
                            # PDF do protocolo
                            if row.get("arquivo_bytes"):
                                pdf_path = f"/tmp/{row['arquivo_nome']}"
                                with open(pdf_path, "wb") as f:
                                    f.write(row["arquivo_bytes"])
                                st.markdown(
                                    f"[📎 Clique aqui para visualizar o PDF do protocolo]({pdf_path})",
                                    unsafe_allow_html=True
                                )
                            else:
                                st.info("Nenhum PDF anexado.")

                            # Informações gerais
                            st.markdown("### 📦 Informações Gerais")
                            st.write(f"👤 **Autor**: {row['autor']} ({row['email']})")
                            st.write(f"🏢 **Departamento**: {row['departamento']} | **Cargo**: {row['cargo']}")
                            st.write(f"📅 **Criado em**: {row['data']} | **Validade**: {row['validade']}")

                            # ▶️ Reagentes com links clicáveis
                            st.markdown("🧪 **Reagentes utilizados**:", unsafe_allow_html=True)
                            if isinstance(row["reagentes"], str):
                                try:
                                    reag_list = eval(row["reagentes"])
                                    links = []
                                    for r in reag_list:
                                        encoded = quote(r)
                                        links.append(
                                            f"[{r}](?aba=🧬 Lista de Reagentes&filtro_reagente={encoded})"
                                        )
                                    st.markdown(", ".join(links), unsafe_allow_html=True)
                                except Exception:
                                    st.markdown(row["reagentes"])
                            else:
                                st.markdown("Nenhum reagente listado.")

                            # Referência
                            st.write(
                                f"🔗 **Referência**: {row['referencia']['autor']}, "
                                f"{row['referencia']['ano']}, DOI: {row['referencia']['doi']}, "
                                f"[Link]({row['referencia']['link']})"
                            )

                            # Comentários
                            st.markdown("### 💬 Comentários")
                            if "comentarios" not in row or not isinstance(row["comentarios"], list):
                                row["comentarios"] = []

                            for c in row["comentarios"]:
                                st.markdown(f"🗨️ **{c['nome']}** ({c['lab']}): {c['texto']}")

                            with st.form(f"form_coment_{row['id']}"):
                                nome = st.text_input("Seu Nome", key=f"nome_{row['id']}")
                                lab = st.text_input("Laboratório", key=f"lab_{row['id']}")
                                texto = st.text_area("Comentário", key=f"coment_{row['id']}")
                                enviar = st.form_submit_button("💬 Adicionar Comentário")
                                if enviar and nome and texto:
                                    novo_comentario = {"nome": nome, "lab": lab, "texto": texto}
                                    for i in range(len(st.session_state.dados)):
                                        if st.session_state.dados.at[i, "id"] == row["id"]:
                                            st.session_state.dados.at[i, "comentarios"].append(novo_comentario)
                                            st.success("Comentário adicionado!")
                                            st.experimental_rerun()

    with col_side:
        st.markdown("### 🕘 Atividades Recentes")
        recentes = df.sort_values("data", ascending=False).head(6)
        for _, row in recentes.iterrows():
            st.markdown(
                f"""
                <div style='border-left: 3px solid #4da6ff; padding-left: 10px; margin-bottom: 15px;'>
                    <div style='font-size:13px;'><b>{row['autor']}</b></div>
                    <div style='font-size:12px;'>📄 <a href='#{quote(row["nome"])}' style='color:#4da6ff;'>{row["nome"]}</a></div>
                    <div style='font-size:11px; color:#999;'>{row["data"]} | ID: {row["id"]}</div>
                </div>
                """,
                unsafe_allow_html=True
            )
