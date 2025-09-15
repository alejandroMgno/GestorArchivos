import streamlit as st
from modules.sdu_module import mostrar_sdu

def main():
    # Configuración de la página
    st.set_page_config(
        page_title="SDU - Sistema de Ubicación",
        page_icon="🔍",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Mostrar directamente el módulo SDU sin login
    mostrar_sdu()

if __name__ == "__main__":
    main()