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
        st.info("Nenhum protocolo cadastrado.")
        return

    # Filtra protocolos de reagentes, se estiverem na mesma tabela
    df = df[df["categoria"] != "🧪 Protocolo de Reagentes/Soluções"]

    st.title("🔬 LabTrack: Plataforma de Controle de Versionamento de Protocolos")
    st.markdown("## Protocolos Cadastrados")

    termo = st.text_input("🔍 Buscar por nome do protocolo")
    if termo:
        df = df[df["nome"].str.contains(termo, case=False, na=False)]

    col_main, col_side = st.columns([4, 1.5])

    # percent-encode do nome da aba
    aba_enc = quote("🧬 Lista de Reagentes", safe="")

    with col_main:
        for grupo in df["grupo"].dropna().unique():
            st.markdown(f"### 🧬 {grupo}")
            gdf = df[df["grupo"] == grupo]
            for cat in gdf["categoria"].dropna().unique():
                st.markdown(f"#### 📁 {cat}")
                cdf = gdf[gdf["categoria"] == cat]
                for _, row in cdf.iterrows():
                    key = f"detalhes_{row['id']}"
                    if key not in st.session_state:
                        st.session_state[key] = False

                    # cartão
                    st.markdown(f"""
                        <div style='border:1px solid #444; border-radius:10px;
                                    padding:10px; margin-bottom:10px; background-color:#111;'>
                            <strong>📄 {row['nome']}</strong><br>
                            <span style='font-size:13px;'>Versão {row['versao']} • {row['data']}</span>
                        </div>
                    """, unsafe_allow_html=True)

                    if st.button("🔍 Ver Detalhes", key=row["id"]):
                        st.session_state[key] = not st.session_state[key]

                    if st.session_state[key]:
                        # PDF
                        if row.get("arquivo_bytes"):
                            tmp = f"/tmp/{row['arquivo_nome']}"
                            with open(tmp, "wb") as f:
                                f.write(row["arquivo_bytes"])
                            st.markdown(f"[📎 Visualizar PDF]({tmp})", unsafe_allow_html=True)
                        else:
                            st.info("Nenhum PDF anexado")

                        # Info gerais
                        st.markdown("### 📦 Informações Gerais")
                        st.write(f"👤 **Autor**: {row['autor']} ({row['email']})")
                        st.write(f"🏢 **Departamento**: {row['departamento']} | **Cargo**: {row['cargo']}")
                        st.write(f"📅 **Criado em**: {row['data']} | **Validade**: {row['validade']}")

                        # ─── Reagentes utilizados ───
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
                            links = []
                            for nome in reag_list:
                                nome_enc = quote(nome, safe="")
                                # AQUI: href começa com "/?..."
                                links.append(
                                    f'<a href="/?aba={aba_enc}&filtro_reagente={nome_enc}" '
                                    f'style="color:#4da6ff; text-decoration:none;">'
                                    f'{nome}</a>'
                                )
                            st.markdown(", ".join(links), unsafe_allow_html=True)
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
                            n = st.text_input("Seu Nome", key=f"nome_{row['id']}")
                            l = st.text_input("Laboratório", key=f"lab_{row['id']}")
                            t = st.text_area("Comentário", key=f"coment_{row['id']}")
                            ok = st.form_submit_button("💬 Adicionar Comentário")
                            if ok and n and t:
                                novo = {"nome": n, "lab": l, "texto": t}
                                for i in range(len(st.session_state.dados)):
                                    if st.session_state.dados.at[i, "id"] == row["id"]:
                                        st.session_state.dados.at[i, "comentarios"].append(novo)
                                        st.success("Comentário adicionado!")
                                        st.experimental_rerun()

    with col_side:
        st.markdown("### 🕘 Atividades Recentes")
        rec = df.sort_values("data", ascending=False).head(6)
        for _, r in rec.iterrows():
            st.markdown(f"""
                <div style='border-left:3px solid #4da6ff; padding-left:10px; margin-bottom:15px;'>
                    <div style='font-size:13px;'><b>{r['autor']}</b></div>
                    <div style='font-size:12px;'>📄 <a href='#{quote(r["nome"])}' style='color:#4da6ff;'>{r['nome']}</a></div>
                    <div style='font-size:11px;color:#999'>{r['data']} | ID: {r['id']}</div>
                </div>
            """, unsafe_allow_html=True)
