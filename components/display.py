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
    # Carrega dados demo se necessário
    if "dados" not in st.session_state or st.session_state.dados.empty:
        st.session_state.dados = carregar_protocolos_demo()

    df = st.session_state.dados
    if df.empty:
        st.info("Nenhum protocolo cadastrado ainda.")
        return

    # Exclui protocolos de reagentes, caso use mesma tabela
    df = df[df["categoria"] != "🧪 Protocolo de Reagentes/Soluções"]

    st.title("🔬 LabTrack: Plataforma de Controle de Versionamento de Protocolos")
    st.markdown("## Protocolos Cadastrados")

    termo = st.text_input("🔍 Buscar por nome do protocolo")
    if termo:
        df = df[df["nome"].str.contains(termo, case=False, na=False)]

    # Prepara base de reagentes (real + demo) para lookup de local
    reagentes_real = st.session_state.get("reagentes", pd.DataFrame())
    if isinstance(reagentes_real, list):
        reagentes_real = pd.DataFrame(reagentes_real)
    reagentes_demo = st.session_state.get("reagentes_demo", pd.DataFrame())
    if isinstance(reagentes_demo, list):
        reagentes_demo = pd.DataFrame(reagentes_demo)
    df_reag = pd.concat([reagentes_real, reagentes_demo], ignore_index=True)

    aba_enc = quote("🧬 Lista de Reagentes", safe="")

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

                    # Cabeçalho
                    st.markdown(f"""
                        <div style='border:1px solid #444; border-radius:10px; 
                                    padding:10px; margin-bottom:10px; background-color:#111;'>
                            <strong>📄 {row['nome']}</strong><br>
                            <span style='font-size:13px;'>Versão {row['versao']} • {row['data']}</span>
                        </div>
                    """, unsafe_allow_html=True)

                    # Botão detalhes
                    if st.button("🔍 Ver Detalhes", key=row["id"]):
                        st.session_state[expand_key] = not st.session_state[expand_key]

                    if st.session_state[expand_key]:
                        # PDF
                        if row.get("arquivo_bytes"):
                            pdf_path = f"/tmp/{row['arquivo_nome']}"
                            with open(pdf_path, "wb") as f:
                                f.write(row["arquivo_bytes"])
                            st.markdown(f"[📎 Clique aqui para visualizar o PDF do protocolo]({pdf_path})", unsafe_allow_html=True)
                        else:
                            st.info("Nenhum PDF anexado.  \n**ADICIONAR UM PDF FICTÍCIO NO DEMO_PROTOCOLS**")

                        # Informações gerais
                        st.markdown("### 📦 Informações Gerais")
                        st.write(f"👤 **Autor**: {row['autor']} ({row['email']})")
                        st.write(f"🏢 **Departamento**: {row['departamento']} | **Cargo**: {row['cargo']}")
                        st.write(f"📅 **Criado em**: {row['data']} | **Validade**: {row['validade']}")

                        # Reagentes utilizados com localização e link
                        st.markdown("🧪 **Reagentes utilizados**:", unsafe_allow_html=True)
                        # Suporta tanto lista quanto string
                        reag_field = row.get("reagentes", [])
                        if isinstance(reag_field, str):
                            try:
                                reag_list = eval(reag_field)
                            except:
                                reag_list = []
                        elif isinstance(reag_field, list):
                            reag_list = reag_field
                        else:
                            reag_list = []

                        if reag_list:
                            html_links = []
                            for nome in reag_list:
                                # Busca a linha no df_reag para capturar local
                                loc = df_reag.loc[df_reag["nome"] == nome, "local"].squeeze()
                                loc_str = f" ({loc})" if pd.notna(loc) and loc else ""
                                enc = quote(nome, safe="")
                                link = (
                                    f'<a href="?aba={aba_enc}&filtro_reagente={enc}" '
                                    f'style="color:#4da6ff; text-decoration:none;">'
                                    f'{nome}</a>'
                                )
                                html_links.append(link + loc_str)
                            st.markdown(", ".join(html_links), unsafe_allow_html=True)
                        else:
                            st.markdown("Nenhum reagente listado.")

                        # Referência
                        ref = row.get("referencia", {})
                        st.write(
                            f"🔗 **Referência**: {ref.get('autor','')}, "
                            f"{ref.get('ano','')}, DOI: {ref.get('doi','')}, "
                            f"[Link]({ref.get('link','')})"
                        )

                        # Comentários
                        st.markdown("### 💬 Comentários")
                        for c in row.get("comentarios", []):
                            st.markdown(f"🗨️ **{c['nome']}** ({c['lab']}): {c['texto']}")

                        # Form de comentário
                        with st.form(f"form_coment_{row['id']}"):
                            nome = st.text_input("Seu Nome", key=f"nome_{row['id']}")
                            lab = st.text_input("Laboratório", key=f"lab_{row['id']}")
                            texto = st.text_area("Comentário", key=f"coment_{row['id']}")
                            enviar = st.form_submit_button("💬 Adicionar Comentário")
                            if enviar and nome and texto:
                                novo = {"nome": nome, "lab": lab, "texto": texto}
                                for i in range(len(st.session_state.dados)):
                                    if st.session_state.dados.at[i, "id"] == row["id"]:
                                        st.session_state.dados.at[i, "comentarios"].append(novo)
                                        st.success("Comentário adicionado!")
                                        st.experimental_rerun()

    # Sidebar de atividades recentes
    with col_side:
        st.markdown("### 🕘 Atividades Recentes")
        recent = df.sort_values("data", ascending=False).head(6)
        for _, r in recent.iterrows():
            st.markdown(
                f"""
                <div style='border-left:3px solid #4da6ff; padding-left:10px; margin-bottom:15px;'>
                    <div style='font-size:13px;'><b>{r['autor']}</b></div>
                    <div style='font-size:12px;'>📄 <a href='#{quote(r["nome"])}' style='color:#4da6ff'>{r["nome"]}</a></div>
                    <div style='font-size:11px;color:#999'>{r['data']} | ID: {r['id']}</div>
                </div>
                """,
                unsafe_allow_html=True
            )
