import streamlit as st
from urllib.parse import quote
import base64
import os
import json
import pandas as pd

def exibir_reagentes():
    st.title("🧬 Lista de Reagentes e Soluções")
    st.markdown("Visualize reagentes já cadastrados ou adicione novos no menu lateral.")

    demo_path = "demo_display/reagentes_demo.json"
    if "reagentes_demo" not in st.session_state:
        if os.path.exists(demo_path):
            try:
                with open(demo_path, "r", encoding="utf-8") as f:
                    reag_demo = json.load(f)
                for r in reag_demo:
                    r["demo"] = True
                    r.setdefault("comentarios", [])
                st.session_state.reagentes_demo = reag_demo
            except Exception:
                st.session_state.reagentes_demo = []
        else:
            st.session_state.reagentes_demo = []

    if "reagentes" not in st.session_state:
        st.session_state.reagentes = []

    # DataFrame → lista de dicts
    reag_real = st.session_state.reagentes
    if isinstance(reag_real, pd.DataFrame):
        reag_real = reag_real.to_dict(orient="records")
    reag_demo = st.session_state.reagentes_demo
    if isinstance(reag_demo, pd.DataFrame):
        reag_demo = reag_demo.to_dict(orient="records")

    reagentes = reag_real + reag_demo

    # Filtro automático via query_params
    filtro = st.experimental_get_query_params().get("filtro_reagente", [""])[0]
    termo = st.text_input("🔍 Buscar reagente por nome", value=filtro)
    if termo:
        reagentes = [r for r in reagentes if termo.lower() in r["nome"].lower()]

    for idx, r in enumerate(reagentes):
        key = f"detalhes_{idx}"
        with st.container():
            st.markdown(
                f"<div style='border:1px solid #666; border-radius:10px;"
                f"padding:10px; margin-bottom:15px; background-color:#111;'>"
                f"<strong>📘 {r['nome']}</strong><br>"
                f"<span style='font-size:13px;'>Validade: {r.get('validade','N/A')}</span>"
                f"</div>",
                unsafe_allow_html=True
            )

            if st.button(f"🔍 Ver detalhes de {r['nome']}", key=key):
                st.session_state[key] = not st.session_state.get(key, False)

            if st.session_state.get(key, False):
                st.markdown("#### 📦 Informações do Reagente")
                st.write(f"👤 **Responsável**: {r.get('responsavel','Desconhecido')}")
                st.write(f"📍 **Local**: {r.get('local','Desconhecido')}")
                st.write(f"🧪 **Componentes**: {r.get('componentes','N/A')}")

                # ——————————————————————————————
                # Se houver PDF (arquivo_bytes), exibe link de visualização
                # ——————————————————————————————
                arquivo_bytes = r.get("arquivo_bytes")
                arquivo_nome  = r.get("arquivo_nome")
                if arquivo_bytes:
                    # se já for base64 string, use diretamente; se for bytes, encode
                    if isinstance(arquivo_bytes, str):
                        b64 = arquivo_bytes
                    else:
                        b64 = base64.b64encode(arquivo_bytes).decode()
                    href = (
                        f'<a href="data:application/pdf;base64,{b64}" target="_blank">'
                        f"📄 Visualizar PDF ({arquivo_nome})</a>"
                    )
                    st.markdown(href, unsafe_allow_html=True)

                st.markdown("##### 💬 Comentários")
                for c in r.get("comentarios", []):
                    st.markdown(f"🗨️ **{c['nome']}** ({c['lab']}): {c['texto']}")

                # — somente adiciona comentários para itens não-demo
                if not r.get("demo"):
                    with st.form(f"form_coment_{idx}"):
                        nome = st.text_input("Seu Nome", key=f"nome_{idx}")
                        lab  = st.text_input("Laboratório", key=f"lab_{idx}")
                        texto= st.text_area("Comentário", key=f"coment_{idx}")
                        enviar = st.form_submit_button("💬 Adicionar Comentário")
                        if enviar and nome and texto:
                            novo = {"nome": nome, "lab": lab, "texto": texto}
                            offset = len(st.session_state.reagentes_demo)
                            i_real = idx - offset
                            if 0 <= i_real < len(st.session_state.reagentes):
                                st.session_state.reagentes[i_real].setdefault("comentarios", []).append(novo)
                                st.success("Comentário adicionado!")
                                st.experimental_rerun()
