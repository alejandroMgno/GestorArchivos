import streamlit as st
import hashlib

def hash_password(password):
    """Hashea una contraseña usando SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def verificar_login(usuario, password):
    """Verifica las credenciales del usuario"""
    USUARIOS = {
        "admin": "240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9",  # admin123
        "usuario": "ecd71870d1963316a97e3ac3408c9835ad8cf0f3c1bc703527c30265534f75ae"  # user123
    }
    
    if usuario in USUARIOS:
        return USUARIOS[usuario] == hash_password(password)
    return False

def mostrar_login():
    """Muestra el formulario de login"""
    st.title("🔐 Sistema de Autenticación")
    st.markdown("---")
    
    with st.form(key='login_form'):
        usuario = st.text_input("Usuario", placeholder="Ingrese su usuario")
        password = st.text_input("Contraseña", placeholder="Ingrese su contraseña", type="password")
        submit = st.form_submit_button("Iniciar Sesión")
        
        if submit:
            if usuario and password:
                if verificar_login(usuario, password):
                    st.session_state.autenticado = True
                    st.session_state.usuario = usuario
                    st.session_state.nombre = "Administrador" if usuario == "admin" else "Usuario"
                    st.success("¡Login exitoso!")
                    return True, usuario
                else:
                    st.error("Credenciales incorrectas")
            else:
                st.warning("Por favor complete todos los campos")
    
    return False, None