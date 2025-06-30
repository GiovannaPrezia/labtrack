import streamlit as st
from urllib.parse import quote, unquote
import base64
import os
import json

def exibir_reagentes():
    df = st.session_state.dados
    demo_path = "demo_display/reagentes_demo.json"

    # Carrega reagentes de demonstração
    if os.path.exists(demo_path):
        try:
            with open(demo_path, "r", encoding="utf-8") as f:
                reag_demo = json.load(f)
            for r in reag_demo:
                r["demo"] = True
            if "reagentes_demo" not in st.session_state:
                st.session_state.reagentes_demo = reag_demo
        except Exception as e:
            st.warning(f"Erro ao carregar reagentes demo: {e}")
            st.session_state.reagentes_demo = []

    reagentes = st.session_state.get("reagentes", []) + st.session_state.get("reagentes_demo", [])

    st.title("🧬 Lista de Reagentes e Soluções")
    st.markdown("Visualize reagentes já cadastrados ou adicione novos no menu lateral.")

    termo = st.text_input("🔍 Buscar reagente por nome")
    if termo:
        reagentes = [r for r in reagentes if termo.lower() in r["nome"].lower()]

    for idx, r in enumerate(reagentes):
        with st.container():
            open_key = f"open_{idx}"
            if open_key not in st.session_state:
                st.session_state[open_key] = False

            st.markdown(
                f"""
                <div style='border:1px solid #666; border-radius:10px; padding:10px; margin-bottom:15px; background-color:#111;'>
                    <strong>📘 {r['nome']}</strong><br>
                    <span style='font-size:13px;'>Validade: {r['validade']}</span><br><br>
                    <a href='#' style='color:#4da6ff;' onclick="document.getElementById('{open_key}').click()">🔍 Ver detalhes</a>
                </div>
                """,
                unsafe_allow_html=True
            )

            if st.button(f"🔍 Ver detalhes de {r['nome']}", key=open_key):
                st.session_state[open_key] = not st.session_state[open_key]

            if st.session_state[open_key]:
                st.markdown("#### 📦 Informações do Reagente")
                st.write(f"👤 **Responsável**: {r['responsavel']}")
                st.write(f"📍 **Local de Armazenamento**: {r['local']}")
                st.write(f"🧪 **Componentes**: {r['componentes']}")

                # Exibir preparo se for PDF
                if r.get("preparo_nome") and r.get("preparo_bytes"):
                    b64 = base64.b64encode(bytes(r["preparo_bytes"])).decode()
                    href = f'<a href="data:application/pdf;base64,{b64}" target="_blank">📄 Visualizar preparo ({r["preparo_nome"]})</a>'
                    st.markdown(href, unsafe_allow_html=True)

                st.markdown("##### 💬 Comentários")
                if "comentarios" not in r or not isinstance(r["comentarios"], list):
                    r["comentarios"] = []

                for c in r["comentarios"]:
                    st.markdown(f"🗨️ **{c['nome']}** ({c['lab']}): {c['texto']}")

                if not r.get("demo"):  # Apenas se for reagente real (não demo)
                    with st.form(f"form_comentario_{idx}"):
                        nome = st.text_input("Seu Nome", key=f"nome_{idx}")
                        lab = st.text_input("Laboratório", key=f"lab_{idx}")
                        texto = st.text_area("Comentário", key=f"coment_{idx}")
                        enviar = st.form_submit_button("💬 Adicionar Comentário")

                        if enviar and nome and texto:
                            novo_comentario = {"nome": nome, "lab": lab, "texto": texto}
                            st.session_state.reagentes[idx - len(st.session_state.get("reagentes_demo", []))]["comentarios"].append(novo_comentario)
                            st.success("Comentário adicionado!")
                            st.experimental_rerun()
