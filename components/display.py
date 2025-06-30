import streamlit as st
import pandas as pd
import base64
import json
from urllib.parse import quote
from pathlib import Path
from datetime import datetime

# —————————————————————————————————————————————
# Carrega os protocolos de demonstração (JSON)
# —————————————————————————————————————————————
@st.cache_data
def carregar_protocolos_demo():
    demo_path = Path("demo_display/protocolos_demo.json")
    if demo_path.exists():
        return pd.DataFrame(json.loads(demo_path.read_text(encoding="utf-8")))
    return pd.DataFrame()

# —————————————————————————————————————————————
# Formulário de cadastro de novo protocolo
# —————————————————————————————————————————————
def form_cadastro():
    st.sidebar.header("➕ Cadastrar Protocolo Novo")
    with st.sidebar.form("form_cadastro"):
        nome      = st.text_input("Nome do Protocolo")
        grupo     = st.text_input("Grupo")
        categoria = st.text_input("Categoria")
        versao    = st.text_input("Versão")
        data      = st.date_input("Data")
        validade  = st.date_input("Validade")
        autor     = st.text_input("Autor")
        email     = st.text_input("Email do Autor")
        depto     = st.text_input("Departamento")
        cargo     = st.text_input("Cargo")
        reagentes = st.text_input("Reagentes (separados por vírgula)")
        # Referência
        ref_autor = st.text_input("Referência: Autor")
        ref_ano   = st.text_input("Referência: Ano")
        ref_doi   = st.text_input("Referência: DOI")
        ref_link  = st.text_input("Referência: Link")
        # PDF ou link externo
        pdf_file  = st.file_uploader("📄 Anexar PDF", type=["pdf"])
        pdf_link  = st.text_input("🌐 Ou link externo para PDF")

        ok = st.form_submit_button("💾 Salvar")
        if ok:
            # Gera ID simples
            novo_id = f"proto{len(st.session_state.dados)+1:03d}"
            # Lê bytes do PDF se houver
            arquivo_bytes = None
            arquivo_nome  = None
            if pdf_file:
                arquivo_bytes = base64.b64encode(pdf_file.read()).decode()
                arquivo_nome  = pdf_file.name
            # Seleciona link externo
            arquivo_link = pdf_link.strip() or None

            novo = {
                "id": novo_id,
                "nome": nome,
                "grupo": grupo,
                "categoria": categoria,
                "versao": versao,
                "data": str(data),
                "validade": str(validade),
                "autor": autor,
                "email": email,
                "departamento": depto,
                "cargo": cargo,
                "reagentes": reagentes,
                "arquivo_nome": arquivo_nome,
                "arquivo_bytes": arquivo_bytes,
                "arquivo_link": arquivo_link,
                "historico": [],
                "referencia": {
                    "autor": ref_autor,
                    "ano": ref_ano,
                    "doi": ref_doi,
                    "link": ref_link
                },
                "comentarios": []
            }

            # Insere no dataframe
            st.session_state.dados = pd.concat(
                [st.session_state.dados, pd.DataFrame([novo])],
                ignore_index=True
            )
            st.success(f"Protocolo '{nome}' cadastrado com sucesso!")

# —————————————————————————————————————————————
# Exibição dos protocolos
# —————————————————————————————————————————————
def exibir_protocolos():
    if "dados" not in st.session_state:
        st.session_state.dados = carregar_protocolos_demo()
    df = st.session_state.dados.copy()
    if df.empty:
        st.info("Nenhum protocolo cadastrado.")
        return

    # Filtra protocolos de reagentes, se necessário
    df = df[df["categoria"] != "🧪 Protocolo de Reagentes/Soluções"]

    st.title("🔬 LabTrack: Protocolos Cadastrados")
    termo = st.text_input("🔍 Buscar por nome do protocolo")
    if termo:
        df = df[df["nome"].str.contains(termo, case=False, na=False)]

    col_main, col_side = st.columns([4, 1.5])
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

                    # Cartão resumido
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
                        # PDF embutido ou link externo
                        if pd.notna(row.get("arquivo_bytes")):
                            pdf_bytes = base64.b64decode(row["arquivo_bytes"])
                            # download
                            st.download_button(
                                "📥 Baixar PDF",
                                data=pdf_bytes,
                                file_name=row["arquivo_nome"],
                                mime="application/pdf"
                            )
                            # embed
                            b64 = row["arquivo_bytes"]
                            html = (f'<iframe src="data:application/pdf;base64,{b64}" '
                                    f'width="100%" height="400px"></iframe>')
                            st.components.v1.html(html, height=400)
                        elif pd.notna(row.get("arquivo_link")):
                            st.markdown(f"[📂 Abrir no Drive]({row['arquivo_link']})")
                        else:
                            st.info("Nenhum PDF anexado nem link externo.")

                        # Informações gerais
                        st.markdown("### 📦 Informações Gerais")
                        st.write(f"👤 **Autor**: {row['autor']} ({row['email']})")
                        st.write(f"🏢 **Departamento**: {row['departamento']} | **Cargo**: {row['cargo']}")
                        st.write(f"📅 **Criado em**: {row['data']} | **Validade**: {row['validade']}")

                        # Reagentes
                        st.markdown("🧪 **Reagentes utilizados**:", unsafe_allow_html=True)
                        raw = row.get("reagentes", "")
                        if isinstance(raw, str):
                            reag_list = [r.strip() for r in raw.split(",") if r.strip()]
                        else:
                            reag_list = raw if isinstance(raw, list) else []
                        if reag_list:
                            links = []
                            for nome in reag_list:
                                nome_enc = quote(nome, safe="")
                                links.append(
                                    f'<a href="/?aba={aba_enc}&filtro_reagente={nome_enc}" '
                                    f'style="color:#4da6ff;">{nome}</a>'
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
                        for c in row.get("comentarios", []):
                            st.markdown(f"🗨️ **{c['nome']}** ({c['lab']}): {c['texto']}")

                        # Formulário de comentário
                        with st.form(f"form_coment_{row['id']}"):
                            n = st.text_input("Seu Nome", key=f"nome_{row['id']}")
                            l = st.text_input("Laboratório", key=f"lab_{row['id']}")
                            t = st.text_area("Comentário", key=f"coment_{row['id']}")
                            ok = st.form_submit_button("💬 Adicionar Comentário")
                            if ok and n and t:
                                novo = {"nome": n, "lab": l, "texto": t}
                                st.session_state.dados.at[
                                    st.session_state.dados["id"] == row["id"], "comentarios"
                                ].iloc[0].append(novo)
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

# —————————————————————————————————————————————
# Execução principal
# —————————————————————————————————————————————
if __name__ == "__main__":
    if "dados" not in st.session_state:
        st.session_state.dados = carregar_protocolos_demo()
    form_cadastro()
    exibir_protocolos()
