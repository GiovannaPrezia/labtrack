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

    # Filtra categorias de reagentes, caso estejam na mesma tabela
    df = df[df["categoria"] != "🧪 Protocolo de Reagentes/Soluções"]

    st.title("🔬 LabTrack: Plataforma de Controle de Versionamento de Protocolos")
    st.markdown("## Protocolos Cadastrados")

    termo = st.text_input("🔍 Buscar por nome do protocolo")
    if termo:
        df = df[df["nome"].str.contains(termo, case=False, na=False)]

    col_main, col_side = st.columns([4, 1.5])

    # codifica o nome exato da aba para usar no link
    aba_enc = quote("🧬 Lista de Reagentes", safe="")

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
                        # Cabeçalho do cartão
                        st.markdown(f"""
                            <div style='border:1px solid #444; border-radius:10px;
                                        padding:10px; margin-bottom:10px; background-color:#111;'>
                                <strong>📄 {row['nome']}</strong><br>
                                <span style='font-size:13px;'>Versão {row['versao']} • {row['data']}</span>
                            </div>
                        """, unsafe_allow_html=True)

                        if st.button("🔍 Ver Detalhes", key=row["id"]):
                            st.session_state[expand_key] = not st.session_state[expand_key]

                        if st.session_state[expand_key]:
                            # Exibe PDF ou sugestão
                            if row.get("arquivo_bytes"):
                                pdf_path = f"/tmp/{row['arquivo_nome']}"
                                with open(pdf_path, "wb") as f:
                                    f.write(row["arquivo_bytes"])
                                st.markdown(
                                    f"[📎 Clique aqui para visualizar o PDF do protocolo]({pdf_path})",
                                    unsafe_allow_html=True
                                )
                            else:
                                st.info("Nenhum PDF anexado")

                            # Informações Gerais
                            st.markdown("### 📦 Informações Gerais")
                            st.write(f"👤 **Autor**: {row['autor']} ({row['email']})")
                            st.write(f"🏢 **Departamento**: {row['departamento']} | **Cargo**: {row['cargo']}")
                            st.write(f"📅 **Criado em**: {row['data']} | **Validade**: {row['validade']}")

                            # ▶️ REAGENTES UTILIZADOS (links clicáveis)
                            st.markdown("🧪 **Reagentes utilizados**:", unsafe_allow_html=True)

                            raw = row.get("reagentes", "")
                            # Converte o campo em lista de nomes
                            if isinstance(raw, str):
                                try:
                                    # se for string de list literal
                                    reag_list = eval(raw)
                                except:
                                    # caso seja "A, B, C"
                                    reag_list = [r.strip() for r in raw.split(",") if r.strip()]
                            elif isinstance(raw, list):
                                reag_list = raw
                            else:
                                reag_list = []

                            if reag_list:
                                links_html = []
                                for nome in reag_list:
                                    enc = quote(nome, safe="")
                                    link = (
                                        f'<a href="?aba={aba_enc}&filtro_reagente={enc}" '
                                        f'style="color:#4da6ff; text-decoration:none;">'
                                        f'{nome}</a>'
                                    )
                                    links_html.append(link)
                                st.markdown(", ".join(links_html), unsafe_allow_html=True)
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
                            if not isinstance(row.get("comentarios", []), list):
                                row["comentarios"] = []
                            for c in row["comentarios"]:
                                st.markdown(f"🗨️ **{c['nome']}** ({c['lab']}): {c['texto']}")

                            # Formulário de novo comentário
                            with st.form(f"form_coment_{row['id']}"):
                                nome = st.text_input("Seu Nome", key=f"nome_{row['id']}")
                                lab = st.text_input("Laboratório", key=f"lab_{row['id']}")
                                texto = st.text_area("Comentário", key=f"coment_{row['id']}")
                                enviar = st.form_submit_button("💬 Adicionar Comentário")
                                if enviar and nome and texto:
                                    novo = {"nome": nome, "lab": lab, "texto": texto}
                                    # adiciona ao session_state.dados
                                    for i in range(len(st.session_state.dados)):
                                        if st.session_state.dados.at[i, "id"] == row["id"]:
                                            st.session_state.dados.at[i, "comentarios"].append(novo)
                                            st.success("Comentário adicionado!")
                                            st.experimental_rerun()

    with col_side:
        st.markdown("### 🕘 Atividades Recentes")
        recentes = df.sort_values("data", ascending=False).head(6)
        for _, row in recentes.iterrows():
            st.markdown(f"""
                <div style='border-left: 3px solid #4da6ff; padding-left: 10px; margin-bottom: 15px;'>
                    <div style='font-size:13px;'><b>{row['autor']}</b></div>
                    <div style='font-size:12px;'>📄 <a href='#{quote(row["nome"])}' style='color:#4da6ff;'>{row["nome"]}</a></div>
                    <div style='font-size:11px; color:#999;'>{row['data']} | ID: {row['id']}</div>
                </div>
            """, unsafe_allow_html=True)
