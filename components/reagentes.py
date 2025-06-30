import streamlit as st
from urllib.parse import quote
import base64
import os
import json
import pandas as pd

def exibir_reagentes():
    st.title("🧬 Lista de Reagentes e Soluções")
    st.markdown("Visualize reagentes já cadastrados ou adicione novos no menu lateral.")

    # Carrega demo de reagentes
    demo_path = "demo_display/reagentes_demo.json"
    if "reagentes_demo" not in st.session_state:
        if os.path.exists(demo_path):
            with open(demo_path, "r", encoding="utf-8") as f:
                reag_demo = json.load(f)
            for r in reag_demo:
                r["demo"] = True
                r.setdefault("comentarios", [])
            st.session_state.reagentes_demo = reag_demo
        else:
            st.session_state.reagentes_demo = []

    # Lista real
    if "reagentes" not in st.session_state:
        st.session_state.reagentes = []

    # Converte DataFrame → list(dict)
    reag_real = st.session_state.reagentes
    if isinstance(reag_real, pd.DataFrame):
        reag_real = reag_real.to_dict("records")
    reag_demo = st.session_state.reagentes_demo
    if isinstance(reag_demo, pd.DataFrame):
        reag_demo = reag_demo.to_dict("records")

    # Remove duplicatas pelo nome
    seen = set()
    reagentes = []
    for r in reag_real + reag_demo:
        if r["nome"] not in seen:
            seen.add(r["nome"])
            reagentes.append(r)

    # Filtro
    filtro = st.query_params.get("filtro_reagente", [""])[0]
    termo  = st.text_input("🔍 Buscar reagente por nome", value=filtro)
    if termo:
        reagentes = [r for r in reagentes if termo.lower() in r["nome"].lower()]

    for idx, r in enumerate(reagentes):
        exp = f"reag_expand_{idx}"
        if exp not in st.session_state:
            st.session_state[exp] = False

        btn = f"reag_btn_{idx}"
        with st.container():
            # Cartão
            st.markdown(
              f"<div style='border:1px solid #666; border-radius:8px; padding:8px; "
              f"margin-bottom:12px; background:#111;'>"
              f"<strong>📘 {r['nome']}</strong><br>"
              f"<span style='font-size:13px;'>Validade: {r.get('validade','N/A')}</span>"
              f"</div>", unsafe_allow_html=True
            )

            if st.button(f"🔍 Ver detalhes de {r['nome']}", key=btn):
                st.session_state[exp] = not st.session_state[exp]

            if st.session_state[exp]:
                # Info gerais
                st.markdown("#### 📦 Informações do Reagente")
                st.write(f"👤 **Responsável**: {r.get('responsavel','-')}")
                st.write(f"📍 **Local**: {r.get('local','-')}")
                st.write(f"🧪 **Componentes**: {r.get('componentes','-')}")

                # PDF embutido
                pb = r.get("arquivo_bytes")
                pn = r.get("arquivo_nome")
                if pb:
                    b64 = pb if isinstance(pb, str) else base64.b64encode(pb).decode()
                    href = (
                      f'<a href="data:application/pdf;base64,{b64}" target="_blank">'
                      f"📄 Ver PDF ({pn})</a>"
                    )
                    st.markdown(href, unsafe_allow_html=True)

                # Link externo, se houver
                link_ext = r.get("arquivo_link")
                if link_ext:
                    st.markdown(f"[📂 Abrir link]({link_ext})", unsafe_allow_html=True)

                # Comentários
                st.markdown("### 💬 Comentários")
                for c in r.get("comentarios", []):
                    st.markdown(f"🗨️ **{c['nome']}** ({c['lab']}): {c['texto']}")

                # Form para novo comentário
                if not r.get("demo"):
                    with st.form(f"form_coment_{idx}"):
                        nome  = st.text_input("Seu Nome", key=f"nome_{idx}")
                        lab   = st.text_input("Laboratório", key=f"lab_{idx}")
                        texto = st.text_area("Comentário",   key=f"coment_{idx}")
                        enviar = st.form_submit_button("💬 Adicionar Comentário")
                        if enviar and nome and texto:
                            novo = {"nome": nome, "lab": lab, "texto": texto}
                            off = len(st.session_state.reagentes_demo)
                            real_i = idx - off
                            if 0 <= real_i < len(st.session_state.reagentes):
                                st.session_state.reagentes[real_i].setdefault("comentarios", []).append(novo)
                                st.success("Comentário adicionado!")
                                st.rerun()
