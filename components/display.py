import streamlit as st

def exibir_protocolos():
    st.header("Protocolos Laboratoriais")

    if st.session_state.dados.empty:
        st.info("Nenhum protocolo cadastrado.")
        return

    for _, row in st.session_state.dados.iterrows():
        with st.expander(f"{row['nome']} (Versão {row['versao']})"):
            st.markdown(f"- **Grupo**: {row['grupo']}")
            st.markdown(f"- **Categoria**: {row['categoria']}")
            st.markdown(f"- **Data**: {row['data']} | **Validade**: {row['validade']}")
            st.markdown(f"- **Autor**: {row['autor']} ({row['email']})")
            st.markdown(f"- **Departamento/Cargo**: {row['departamento']} / {row['cargo']}")
            st.markdown(f"- **Reagentes**: {', '.join(eval(row['reagentes'])) if isinstance(row['reagentes'], str) else ''}")
            
            if row['arquivo_nome']:
                st.download_button(
                    label="📎 Baixar Protocolo",
                    data=row['arquivo_bytes'],
                    file_name=row['arquivo_nome']
                )
            
            # Referência
            st.markdown("**Referência**:")
            st.markdown(f"{row.get('referencia_autor', '')}, {row.get('referencia_ano', '')}, {row.get('referencia_doi', '')}")

            # Comentário
            if row.get("comentario_texto"):
                st.markdown("**Comentário:**")
                st.markdown(f"_Por {row.get('comentario_nome', '')} ({row.get('comentario_lab', '')})_")
                st.info(row["comentario_texto"])
