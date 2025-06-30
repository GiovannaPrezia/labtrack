import streamlit as st
import pandas as pd
from urllib.parse import quote
from pathlib import Path
import json

def carregar_protocolos_demo():
    try:
        p = Path("demo_display/protocolos_demo.json")
        return pd.DataFrame(json.load(p.open("r", encoding="utf-8")))
    except Exception as e:
        st.warning(f"Erro ao carregar protocolos demo: {e}")
        return pd.DataFrame()

def exibir_protocolos():
    if "dados" not in st.session_state or st.session_state.dados.empty:
        st.session_state.dados = carregar_protocolos_demo()

    df = st.session_state.dados
    if df.empty:
        st.info("Nenhum protocolo cadastrado.")
        return

    df = df[df["categoria"]!="🧪 Protocolo de Reagentes/Soluções"]

    st.title("🔬 LabTrack: Plataforma de Controle de Versionamento de Protocolos")
    termo = st.text_input("🔍 Buscar por nome do protocolo")
    if termo:
        df = df[df["nome"].str.contains(termo, case=False, na=False)]

    col_main, col_side = st.columns([4,1.5])
    aba_enc = quote("🧬 Lista de Reagentes", safe="")

    with col_main:
        for grupo in df["grupo"].dropna().unique():
            st.markdown(f"### 🧬 {grupo}")
            gdf = df[df["grupo"]==grupo]
            for cat in gdf["categoria"].dropna().unique():
                st.markdown(f"#### 📁 {cat}")
                cdf = gdf[gdf["categoria"]==cat]
                for _, row in cdf.iterrows():
                    key = f"det_{row['id']}"
                    if key not in st.session_state:
                        st.session_state[key]=False

                    st.markdown(
                        f"<div style='border:1px solid #444; border-radius:10px; "
                        f"padding:10px; margin-bottom:10px; background-color:#111;'>"
                        f"<strong>📄 {row['nome']}</strong><br>"
                        f"<span style='font-size:13px;'>Versão {row['versao']} • {row['data']}</span>"
                        f"</div>",
                        unsafe_allow_html=True
                    )

                    if st.button("🔍 Ver Detalhes", key=row["id"]):
                        st.session_state[key]=not st.session_state[key]

                    if st.session_state[key]:
                        # PDF
                        if row.get("arquivo_bytes"):
                            path=f"/tmp/{row['arquivo_nome']}"
                            open(path,"wb").write(row["arquivo_bytes"])
                            st.markdown(f"[📎 PDF]({path})",unsafe_allow_html=True)
                        else:
                            st.info("Nenhum PDF anexado.")

                        # Info gerais
                        st.markdown("### 📦 Informações Gerais")
                        st.write(f"👤 **Autor**: {row['autor']} ({row['email']})")
                        st.write(f"🏢 **Departamento**: {row['departamento']} | **Cargo**: {row['cargo']}")
                        st.write(f"📅 **Criado em**: {row['data']} | **Validade**: {row['validade']}")

                        # Reagentes clicáveis
                        st.markdown("🧪 **Reagentes utilizados**:", unsafe_allow_html=True)
                        try:
                            lst = eval(row["reagentes"])
                        except:
                            lst = []
                        if lst:
                            links = []
                            for r in lst:
                                en = quote(r, safe="")
                                links.append(
                                    f'<a href="?aba={aba_enc}&filtro_reagente={en}" '
                                    f'style="color:#4da6ff;text-decoration:none">{r}</a>'
                                )
                            st.markdown(", ".join(links), unsafe_allow_html=True)
                        else:
                            st.markdown("Nenhum reagente listado.")

                        # Referência
                        ref = row["referencia"]
                        st.write(f"🔗 **Referência**: {ref['autor']}, {ref['ano']}, DOI: {ref['doi']}, [Link]({ref['link']})")

                        # Comentários
                        st.markdown("### 💬 Comentários")
                        cmts = row.get("comentarios", [])
                        for c in cmts:
                            st.markdown(f"🗨️ **{c['nome']}** ({c['lab']}): {c['texto']}")

                        with st.form(f"form_coment_{row['id']}"):
                            nome=st.text_input("Seu Nome", key=f"nme_{row['id']}")
                            lab = st.text_input("Laboratório", key=f"lab_{row['id']}")
                            tx  = st.text_area("Comentário", key=f"cmt_{row['id']}")
                            ok  = st.form_submit_button("💬 Adicionar Comentário")
                            if ok and nome and tx:
                                new={"nome":nome,"lab":lab,"texto":tx}
                                for i in range(len(st.session_state.dados)):
                                    if st.session_state.dados.at[i,"id"]==row["id"]:
                                        st.session_state.dados.at[i,"comentarios"].append(new)
                                        st.success("Comentário adicionado!")
                                        st.experimental_rerun()

    with col_side:
        st.markdown("### 🕘 Atividades Recentes")
        recent = df.sort_values("data",ascending=False).head(6)
        for _, r in recent.iterrows():
            st.markdown(
                f"<div style='border-left:3px solid #4da6ff; padding-left:10px; margin-bottom:15px;'>"
                f"<div style='font-size:13px;'><b>{r['autor']}</b></div>"
                f"<div style='font-size:12px;'>📄 <a href='#{quote(r['nome'],safe='')}' "
                f"style='color:#4da6ff'>{r['nome']}</a></div>"
                f"<div style='font-size:11px;color:#999'>{r['data']} | ID: {r['id']}</div>"
                f"</div>",
                unsafe_allow_html=True
            )
