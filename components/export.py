import streamlit as st

def exportar_dados():
    st.header("Exportar Dados")

    if not st.session_state.dados.empty:
        csv = st.session_state.dados.to_csv(index=False)
        st.download_button("📥 Baixar Protocolos (.csv)", data=csv, file_name="protocolos.csv", mime="text/csv")
    else:
        st.info("Nenhum protocolo para exportar.")

    if not st.session_state.reagentes.empty:
        csv_reagentes = st.session_state.reagentes.to_csv(index=False)
        st.download_button("📥 Baixar Reagentes (.csv)", data=csv_reagentes, file_name="reagentes.csv", mime="text/csv")
