import streamlit as st
from streamlit.components.v1 import html
import base64
import os

def exibir_mapa():
    st.title("🗺️ Mapa do Laboratório")

    # 1) Carrega a imagem (PNG) em base64
    img_path = os.path.join("demo_display", "mapa_lab.png")  # ou onde você guardou
    with open(img_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()

    # 2) HTML com <map> e <area> definindo as regiões clicáveis
    #    Ajuste coords para cada retângulo
    html_code = f'''
    <img 
      src="data:image/png;base64,{b64}" 
      usemap="#labmap"
      style="max-width:100%; height:auto;"
    />
    <map name="labmap">
      <!-- exemplo de área -->
      <area
        shape="rect"
        coords="550,650,950,850"
        alt="bancada_grande"
        onclick="Streamlit.setComponentValue('bancada_grande')"
      />
      <!-- repita para: arm_superior_1, arm_inferior_2, freezer_-80, guarda_jaleco, etc. -->
    </map>
    '''
    # 3) Renderiza e captura o retorno
    selecionado = html(html_code, height=900)

    if selecionado:
        st.success(f"Você clicou em: **{selecionado}**")
        # aqui você pode filtrar seus dados:
        # df = st.session_state.dados.query("local == @selecionado")
        # st.dataframe(df)
