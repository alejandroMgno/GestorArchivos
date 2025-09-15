import streamlit as st
from modules.auth import mostrar_login
from modules.sdu_module import mostrar_sdu

def main():
    # Configuración de la página
    st.set_page_config(
        page_title="Sistema Corporativo",
        page_icon= "./assets/images.jpeg",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Inicializar variables de sesión
    if 'autenticado' not in st.session_state:
        st.session_state.autenticado = False
        st.session_state.usuario = None
        st.session_state.nombre = None
        st.session_state.app_seleccionada = "SDU - Sistema de Ubicación"
        st.session_state.datos_cargados = False
    
    # Mostrar login si no está autenticado
    if not st.session_state.autenticado:
        autenticado, usuario = mostrar_login()
        if autenticado:
            # Limpiar y recargar
            st.session_state.autenticado = True
            st.experimental_rerun()
        return
    
    # CONTENIDO PRINCIPAL (autenticado)
    
    # Sidebar
    with st.sidebar:
        st.sidebar.image("./assets/images.jpeg", use_container_width=True)
        st.title("Sistema Corporativo")
        st.markdown(f"Bienvenido: **{st.session_state.nombre}**")
        st.markdown(f"Usuario: `{st.session_state.usuario}`")
        st.markdown("---")
        
        st.subheader("Aplicaciones Disponibles")
        
        # Navegación
        opciones = ["SDU - Sistema de Ubicación", "Dashboard"]
        opcion_seleccionada = st.radio("Seleccione:", opciones, index=0)
        
        st.markdown("---")
        
        if st.button("🚪 Cerrar Sesión", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.success("Sesión cerrada")
            st.experimental_rerun()
        
        st.info("Sistema Corporativo v1.0")
    
    # Contenido principal
    if "SDU" in opcion_seleccionada:
        mostrar_sdu()
    else:
        st.title(opcion_seleccionada)
        st.info("Esta funcionalidad estará disponible próximamente")

if __name__ == "__main__":
    main()