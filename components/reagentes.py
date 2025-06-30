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

    # —— Carrega reagentes de demonstração se necessário ——
    if "reagentes_demo" not in st.session_state:
        if os.path.exists(demo_path):
            try:
                with open(demo_path, "r", encoding="utf-8") as f:
                    reag_demo = json.load(f)
                for r in reag_demo:
                    r["demo"] = True
                    if "comentarios" not in r:
                        r["comentarios"] = []
                st.session_state.reagentes_demo = reag_demo
            except Exception as e:
                st.warning(f"Erro ao carregar reagentes demo: {e}")
                st.session_state.reagentes_demo = []
        else:
            st.session_state.reagentes_demo = []

    # —— Garante que haja uma lista de reagentes reais ——
    if "reagentes" not in st.session_state:
        st.session_state.reagentes = []

    # Converte DataFrame → lista de dicts, se for o caso
    reag_real = st.session_state.reagentes
    if isinstance(reag_real, pd.DataFrame):
        reag_real = reag_real.to_dict(orient="records")

    reag_demo = st.session_state.reagentes_demo
    if isinstance(reag_demo, pd.DataFrame):
        reag_demo = reag_demo.to_dict(orient="records")

    reagentes = reag_real + reag_demo

    # —— Filtro automático via URL ——
    query_params = st.query_params
    filtro = query_params.get("filtro_reagente", [""])[0]

    termo = st.text_input("🔍 Buscar reagente por nome", value=filtro)
    if termo:
        reagentes = [r for r in reagentes if termo.lower() in r["nome"].lower()]

    # —— Exibição dos reagentes ——
    for idx, r in enumerate(reagentes):
        bloco_key = f"detalhes_{idx}"

        with st.container():
            st.markdown(
                f"""
                <div style='border:1px solid #666; border-radius:10px; 
                            padding:10px; margin-bottom:15px; background-color:#111;'>
                    <strong>📘 {r['nome']}</strong><br>
                    <span style='font-size:13px;'>Validade: {r.get('validade', 'N/A')}</span><br><br>
                </div>
                """,
                unsafe_allow_html=True
            )

            if st.button(f"🔍 Ver detalhes de {r['nome']}", key=f"btn_{idx}"):
                st.session_state[bloco_key] = not st.session_state.get(bloco_key, False)

            if st.session_state.get(bloco_key, False):
                st.markdown("#### 📦 Informações do Reagente")
                st.write(f"👤 **Responsável**: {r.get('responsavel', 'Desconhecido')}")
                st.write(f"📍 **Local de Armazenamento**: {r.get('local', 'Desconhecido')}")
                st.write(f"🧪 **Componentes**: {r.get('componentes', 'N/A')}")

                # PDF de preparo (se existir)
                if r.get("preparo_nome") and r.get("preparo_bytes"):
                    b64 = base64.b64encode(bytes(r["preparo_bytes"])).decode()
                    href = (
                        f'<a href="data:application/pdf;base64,{b64}" '
                        f'target="_blank">📄 Visualizar preparo ({r["preparo_nome"]})</a>'
                    )
                    st.markdown(href, unsafe_allow_html=True)

                st.markdown("##### 💬 Comentários")
                for c in r.get("comentarios", []):
                    st.markdown(f"🗨️ **{c['nome']}** ({c['lab']}): {c['texto']}")

                if not r.get("demo"):
                    with st.form(f"form_comentario_{idx}"):
                        nome = st.text_input("Seu Nome", key=f"nome_{idx}")
                        lab = st.text_input("Laboratório", key=f"lab_{idx}")
                        texto = st.text_area("Comentário", key=f"coment_{idx}")
                        enviar = st.form_submit_button("💬 Adicionar Comentário")

                        if enviar and nome and texto:
                            novo_comentario = {"nome": nome, "lab": lab, "texto": texto}
                            offset = len(st.session_state.reagentes_demo)
                            index_real = idx - offset
                            if 0 <= index_real < len(st.session_state.reagentes):
                                st.session_state.reagentes[index_real].setdefault("comentarios", []).append(novo_comentario)
                                st.success("Comentário adicionado!")
                                st.experimental_rerun()
