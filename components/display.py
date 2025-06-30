import streamlit as st
import pandas as pd
import base64
import json
from urllib.parse import quote
from pathlib import Path

@st.cache_data
def carregar_protocolos_demo():
    demo_path = Path("demo_display/protocolos_demo.json")
    if demo_path.exists():
        return pd.DataFrame(json.loads(demo_path.read_text(encoding="utf-8")))
    return pd.DataFrame()

def exibir_protocolos():
    if "dados" not in st.session_state:
        st.session_state.dados = carregar_protocolos_demo()
    df = st.session_state.dados.copy()
    if df.empty:
        st.info("Nenhum protocolo cadastrado.")
        return

    st.title("🔬 LabTrack: Protocolos Cadastrados")
    termo = st.text_input("🔍 Buscar por nome do protocolo")
    if termo:
        df = df[df["nome"].str.contains(termo, case=False, na=False)]

    for _, row in df.iterrows():
        st.markdown(f"---\n### 📄 {row['nome']}  \n"
                    f"**Versão** {row['versao']} • **Data** {row['data']}")
        
        # Só botão de download do PDF embutido
        if pd.notna(row.get("arquivo_bytes")):
            pdf_bytes = base64.b64decode(row["arquivo_bytes"])
            st.download_button(
                "📥 Baixar PDF",
                data=pdf_bytes,
                file_name=row["arquivo_nome"],
                mime="application/pdf"
            )
        # Ou, se tiver link externo, ofereça download via link
        elif pd.notna(row.get("arquivo_link")):
            st.markdown(f"[📂 Baixar PDF Externo]({row['arquivo_link']})")
        else:
            st.info("Nenhum PDF anexado nem link externo.")

        # Demais metadados
        st.write(f"👤 **Autor**: {row['autor']} ({row['email']})")
        st.write(f"🏢 **Departamento**: {row['departamento']} | **Cargo**: {row['cargo']}")
        st.write(f"🧪 **Reagentes**: {row['reagentes']}")
        ref = row.get("referencia", {})
        st.write(f"🔗 **Referência**: {ref.get('autor','')}, {ref.get('ano','')}, DOI {ref.get('doi','')}, [Link]({ref.get('link','')})")

if __name__ == "__main__":
    exibir_protocolos()
