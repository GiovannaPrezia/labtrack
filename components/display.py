import streamlit as st
import pandas as pd
from urllib.parse import quote
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
        st.info("Nenhum protocolo cadastrado.")
        return

    # Filtra para não mostrar protocolos de reagentes
    df = df[df["categoria"] != "🧪 Protocolo de Reagentes/Soluções"]

    st.title("🔬 LabTrack: Plataforma de Controle de Versionamento de Protocolos")
    termo = st.text_input("🔍 Buscar por nome do protocolo")
    if termo:
        df = df[df["nome"].str.contains(termo, case=False, na=False)]

    col_main, col_side = st.columns([4, 1.5])
    with col_main:
        for grupo in df["grupo"].dropna().unique():
            st.markdown(f"### 🧬 {grupo}")
            gdf = df[df["grupo"] == grupo]
            for cat in gdf["categoria"].dropna().unique():
                st.markdown(f"#### 📁 {cat}")
                cdf = gdf[gdf["categoria"] == cat]

                for _, row in cdf.iterrows():
                    det_key = f"det_{row['id']}"
                    if det_key not in st.session_state:
                        st.session_state[det_key] = False

                    st.markdown(
                        f"<div style='border:1px solid #444; border-radius:10px;"
                        f" padding:10px; margin-bottom:10px; background-color:#111;'>"
                        f"<strong>📄 {row['nome']}</strong><br>"
                        f"<span style='font-size:13px;'>Versão {row['versao']} • {row['data']}</span>"
                        f"</div>",
                        unsafe_allow_html=True
                    )

                    if st.button("🔍 Ver Detalhes", key=row["id"]):
                        st.session_state[det_key] = not st.session_state[det_key]

                    if st.session_state[det_key]:
                        # PDF
                        if row.get("arquivo_bytes"):
                            tmp = f"/tmp/{row['arquivo_nome']}"
                            with open(tmp, "wb") as f:
                                f.write(row["arquivo_bytes"])
                            st.markdown(f"[📎 Visualizar PDF]({tmp})", unsafe_allow_html=True)
                        else:
                            st.info("Nenhum PDF anexado.  \n**ADICIONAR UM PDF FICTÍCIO NO DEMO_PROTOCOLS**")

                        # Info gerais
                        st.markdown("### 📦 Informações Gerais")
                        st.write(f"👤 **Autor**: {row['autor']} ({row['email']})")
                        st.write(f"🏢 **Departamento**: {row['departamento']} | **Cargo**: {row['cargo']}")
                        st.write(f"📅 **Criado em**: {row['data']} | **Validade**: {row['validade']}")

                        # REAGENTES UTILIZADOS: botões que redirecionam
                        st.markdown("🧪 **Reagentes utilizados**:", unsafe_allow_html=True)
                        raw = row.get("reagentes", "")
                        if isinstance(raw, str):
                            try:
                                reag_list = eval(raw)
                            except:
                                reag_list = [r.strip() for r in raw.split(",") if r.strip()]
                        elif isinstance(raw, list):
                            reag_list = raw
                        else:
                            reag_list = []

                        if reag_list:
                            for nome in reag_list:
                                # ao clicar, seta os query_params e recarrega na aba reagentes
                                if st.button(f"➡️ {nome}", key=f"link_{row['id']}_{nome}"):
                                    st.experimental_set_query_params(
                                        aba="🧬 Lista de Reagentes",
                                        filtro_reagente=nome
                                    )
                                    st.experimental_rerun()
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
                        comentarios = row.get("comentarios", [])
                        if not isinstance(comentarios, list):
                            comentarios = []
                        for c in comentarios:
                            st.markdown(f"🗨️ **{c['nome']}** ({c['lab']}): {c['texto']}")

                        # Form comentário
                        with st.form(f"form_coment_{row['id']}"):
                            n = st.text_input("Seu Nome", key=f"n_{row['id']}")
                            l = st.text_input("Laboratório", key=f"l_{row['id']}")
                            t = st.text_area("Comentário", key=f"t_{row['id']}")
                            ok = st.form_submit_button("💬 Adicionar Comentário")
                            if ok and n and t:
                                novo = {"nome": n, "lab": l, "texto": t}
                                for i in range(len(st.session_state.dados)):
                                    if st.session_state.dados.at[i, "id"] == row["id"]:
                                        st.session_state.dados.at[i, "comentarios"].append(novo)
                                        st.succes
