import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import re
from io import BytesIO
import urllib3
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import time
import os

# Desactivar warnings de SSL para desarrollo
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Configuración de la página con layout más ancho
st.set_page_config(
    page_title="SDU - Sistema de Ubicación",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSS personalizado para reducir márgenes al máximo
st.markdown("""
    <style>
    /* Reducir márgenes principales al mínimo */
    .main .block-container {
        padding-top: 0.5rem !important;
        padding-bottom: 0.5rem !important;
        padding-left: 0.5rem !important;
        padding-right: 0.5rem !important;
        max-width: 100% !important;
    }
    
    /* Header más compacto */
    header .decoration {
        padding: 0.25rem 0.5rem !important;
    }
    
    /* Expanders más compactos */
    .stExpander {
        margin-bottom: 0.25rem !important;
    }
    
    /* Columnas más compactas */
    .stColumns {
        gap: 0.25rem !important;
    }
    
    /* Botones más compactos */
    .stButton button {
        width: 100%;
        margin: 0.1rem 0 !important;
        padding: 0.25rem 0.5rem !important;
    }
    
    /* Inputs más compactos */
    .stTextInput input {
        padding: 0.25rem !important;
        margin: 0.1rem 0 !important;
    }
    
    /* Dataframes más compactos */
    .dataframe {
        width: 100% !important;
        margin: 0.25rem 0 !important;
    }
    
    /* Reducir padding interno de las celdas */
    .dataframe th, .dataframe td {
        padding: 1px 2px !important;
        font-size: 0.8em !important;
    }
    
    /* Tabs más compactos */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0 !important;
    }
    
    .stTadsadasb [data-baseweb="tab"] {
        padding: 0.25rem 0.5rem !important;
        font-size: 0.9em !important;
    }
    
    /* Reducir espacio entre elementos */
    .element-container {
        padding: 0.1rem 0 !important;
        margin: 0.1rem 0 !important;
    }
    
    /* Ajustar el ancho máximo del contenido principal */
    .main .block-container {
        max-width: 99vw !important;
    }
    
    /* Eliminar márgenes adicionales */
    div[data-testid="stVerticalBlock"] > div[style*="flex-direction: column;"] > div {
        margin: 0.1rem 0 !important;
    }
    
    /* Info messages más compactos */
    .stAlert {
        padding: 0.25rem !important;
        margin: 0.1rem 0 !important;
    }
    
    /* Success messages más compactos */
    .stSuccess {
        padding: 0.25rem !important;
        margin: 0.1rem 0 !important;
    }
    
    /* Error messages más compactos */
    .stError {
        padding: 0.25rem !important;
        margin: 0.1rem 0 !important;
    }
    
    /* File uploader más compacto */
    .stFileUploader {
        margin: 0.1rem 0 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# Directorio temporal para guardar archivos
TEMP_DIR = "temp_archivos"
if not os.path.exists(TEMP_DIR):
    os.makedirs(TEMP_DIR)

# Contraseña para ver empleados no encontrados y actualizar archivos
PASSWORD = "admin2021*+"

def guardar_archivo_temporal(uploaded_file, tipo_archivo):
    """Guarda un archivo subido en el directorio temporal"""
    if uploaded_file is not None:
        # Eliminar archivo anterior si existe
        for archivo in os.listdir(TEMP_DIR):
            if archivo.startswith(tipo_archivo):
                os.remove(os.path.join(TEMP_DIR, archivo))
        
        # Guardar nuevo archivo
        file_path = os.path.join(TEMP_DIR, f"{tipo_archivo}_{uploaded_file.name}")
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getvalue())
        return file_path
    return None

def cargar_archivo_temporal(tipo_archivo):
    """Carga un archivo desde el directorio temporal"""
    for archivo in os.listdir(TEMP_DIR):
        if archivo.startswith(tipo_archivo):
            return os.path.join(TEMP_DIR, archivo)
    return None

def archivos_temporales_existen():
    """Verifica si existen archivos temporales guardados"""
    tipos = ['ubicacion', 'correo', 'telefono']
    return all(cargar_archivo_temporal(tipo) is not None for tipo in tipos)

def limpiar_archivos_temporales():
    """Elimina todos los archivos temporales"""
    for archivo in os.listdir(TEMP_DIR):
        os.remove(os.path.join(TEMP_DIR, archivo))

def create_session():
    """Crea una sesión HTTP con reintentos"""
    session = requests.Session()
    retry_strategy = Retry(
        total=3,
        backoff_factor=0.1,
        status_forcelist=[429, 500, 502, 503, 504],
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session

def cargar_archivo_desde_ruta(file_path, header_row=0):
    """Carga un archivo Excel desde una ruta de archivo"""
    try:
        if file_path and os.path.exists(file_path):
            df = pd.read_excel(file_path, header=header_row, engine='openpyxl')
            
            # Limpiar nombres de columnas
            df.columns = df.columns.astype(str).str.strip().str.lower().str.replace(' ', '_')
            df.columns = df.columns.str.replace(r'[^\w_]', '', regex=True)
            
            # Eliminar filas completamente vacías
            df = df.dropna(how='all')
            
            return df
        return None
    except Exception as e:
        st.error(f"❌ Error al cargar el archivo desde {file_path}: {str(e)}")
        return None

def limpiar_nombres_columnas(columnas):
    """Limpia y normaliza los nombres de las columnas"""
    columnas_limpias = []
    for col in columnas:
        col_limpio = str(col).strip().lower()
        col_limpio = re.sub(r'[^\w\s]', '', col_limpio)
        col_limpio = re.sub(r'\s+', '_', col_limpio)
        columnas_limpias.append(col_limpio)
    return columnas_limpias

def encontrar_columna_clave(df, posibles_nombres):
    """Encuentra la primera columna que coincida con los nombres clave"""
    if df is None or df.empty:
        return None
        
    df_columns_clean = limpiar_nombres_columnas(df.columns)
    
    for nombre in posibles_nombres:
        for i, col in enumerate(df_columns_clean):
            if nombre in col:
                return df.columns[i]  # Devolver el nombre original de la columna
    
    return None

def es_director(puesto):
    """Verifica si el puesto es director (excluyendo subdirector)"""
    if pd.isna(puesto) or puesto == '':
        return False
    
    puesto_str = str(puesto).lower().strip()
    
    # Buscar la palabra "director" pero excluir "subdirector"
    if 'director' in puesto_str and 'subdirector' not in puesto_str:
        return True
    
    return False

def procesar_datos(df_ubicacion, df_correo, df_telefono, progress_bar=None):
    """Procesa y combina los datos de los tres archivos con barra de progreso"""
    try:
        if df_ubicacion is None or df_correo is None or df_telefono is None:
            return None
        
        if progress_bar:
            progress_bar.progress(0.1, text="🔍 Buscando columnas...")
        
        # Listas de posibles nombres para cada campo
        posibles_nombres_nombre = ['nombre', 'name', 'nombres', 'empleado', 'colaborador']
        posibles_nombres_puesto = ['puesto', 'cargo', 'position', 'job_title']
        posibles_nombres_departamento = ['departamento', 'area', 'department', 'depto']
        posibles_nombres_telefono = ['telefono', 'tel', 'phone', 'celular', 'movil']
        posibles_nombres_correo = ['correo', 'email', 'mail']
        
        # Encontrar columnas clave en cada archivo
        col_nombre_ubi = encontrar_columna_clave(df_ubicacion, posibles_nombres_nombre)
        col_nombre_correo = encontrar_columna_clave(df_correo, posibles_nombres_nombre)
        col_nombre_telefono = encontrar_columna_clave(df_telefono, posibles_nombres_nombre)
        
        col_puesto_ubi = encontrar_columna_clave(df_ubicacion, posibles_nombres_puesto)
        col_departamento_ubi = encontrar_columna_clave(df_ubicacion, posibles_nombres_departamento)
        
        # Encontrar columnas de teléfono y correo en sus respectivos archivos
        columnas_telefono = [col for col in df_telefono.columns if any(tel in str(col).lower() for tel in posibles_nombres_telefono)]
        columnas_correo = [col for col in df_correo.columns if any(mail in str(col).lower() for mail in posibles_nombres_correo)]
        
        # Validar columnas
        if not col_nombre_ubi:
            st.error("❌ No se encontró columna de 'nombre' en el archivo de ubicación")
            return None
        
        if not col_nombre_correo:
            st.error("❌ No se encontró columna de 'nombre' in el archivo de correo")
            return None
            
        if not col_nombre_telefono:
            st.error("❌ No se encontró columna de 'nombre' en el archivo de teléfono")
            return None
        
        # Limpiar and estandarizar datos
        df_ubicacion_clean = df_ubicacion.copy()
        df_correo_clean = df_correo.copy()
        df_telefono_clean = df_telefono.copy()
        
        if progress_bar:
            progress_bar.progress(0.3, text="🧹 Limpiando datos...")
        
        # Limpiar columna de nombre en todos los archivos
        df_ubicacion_clean[col_nombre_ubi] = df_ubicacion_clean[col_nombre_ubi].astype(str).str.strip().str.upper()
        df_correo_clean[col_nombre_correo] = df_correo_clean[col_nombre_correo].astype(str).str.strip().str.upper()
        df_telefono_clean[col_nombre_telefono] = df_telefono_clean[col_nombre_telefono].astype(str).str.strip().str.upper()
        
        # Eliminar valores inválidos
        df_ubicacion_clean = df_ubicacion_clean[df_ubicacion_clean[col_nombre_ubi] != 'NAN']
        df_ubicacion_clean = df_ubicacion_clean[df_ubicacion_clean[col_nombre_ubi] != 'NONE']
        df_ubicacion_clean = df_ubicacion_clean[~df_ubicacion_clean[col_nombre_ubi].isna()]
        df_ubicacion_clean = df_ubicacion_clean[df_ubicacion_clean[col_nombre_ubi] != '']
        
        df_correo_clean = df_correo_clean[df_correo_clean[col_nombre_correo] != 'NAN']
        df_correo_clean = df_correo_clean[df_correo_clean[col_nombre_correo] != 'NONE']
        df_correo_clean = df_correo_clean[~df_correo_clean[col_nombre_correo].isna()]
        df_correo_clean = df_correo_clean[df_correo_clean[col_nombre_correo] != '']
        
        df_telefono_clean = df_telefono_clean[df_telefono_clean[col_nombre_telefono] != 'NAN']
        df_telefono_clean = df_telefono_clean[df_telefono_clean[col_nombre_telefono] != 'NONE']
        df_telefono_clean = df_telefono_clean[~df_telefono_clean[col_nombre_telefono].isna()]
        df_telefono_clean = df_telefono_clean[df_telefono_clean[col_nombre_telefono] != '']
        
        if progress_bar:
            progress_bar.progress(0.5, text="🔗 Combinando datos...")
        
        # Crear diccionarios para puestos y departamentos
        puesto_dict = {}
        departamento_dict = {}
        
        if col_puesto_ubi:
            for _, row in df_ubicacion_clean.iterrows():
                nombre = row[col_nombre_ubi]
                puesto_dict[nombre] = row.get(col_puesto_ubi, '')
        
        if col_departamento_ubi:
            for _, row in df_ubicacion_clean.iterrows():
                nombre = row[col_nombre_ubi]
                departamento_dict[nombre] = row.get(col_departamento_ubi, '')
        
        # Crear diccionarios para correos y teléfonos
        correo_dict = {}
        telefono_dict = {}
        
        # Procesar correos
        for _, row in df_correo_clean.iterrows():
            nombre = row[col_nombre_correo]
            for col in columnas_correo:
                if col in row and pd.notna(row[col]) and str(row[col]).strip() != '':
                    correo_dict[nombre] = row[col]
                    break
        
        # Procesar teléfonos
        for _, row in df_telefono_clean.iterrows():
            nombre = row[col_nombre_telefono]
            for col in columnas_telefono:
                if col in row and pd.notna(row[col]) and str(row[col]).strip() != '':
                    telefono_dict[nombre] = row[col]
                    break
        
        # Crear el dataframe combinado - SOLO EMPLEADOS EN UBICACIÓN
        datos_combinados = []
        
        for nombre in df_ubicacion_clean[col_nombre_ubi].values:
            # Solo incluir empleados que están en ubicación
            if nombre in df_ubicacion_clean[col_nombre_ubi].values:
                # Obtener datos de cada fuente
                puesto = puesto_dict.get(nombre, '')
                departamento = departamento_dict.get(nombre, '')
                correo = correo_dict.get(nombre, '')
                telefono = telefono_dict.get(nombre, '')
                
                # Solo incluir si tiene teléfono o correo
                if telefono != '' or correo != '':
                    datos_combinados.append({
                        'nombre': nombre,
                        'departamento': departamento,
                        'puesto': puesto,
                        'correo': correo,
                        'telefono': telefono
                    })
        
        df_combinado = pd.DataFrame(datos_combinados)
        
        # Asegurar el orden correcto de las columnas
        column_order = ['nombre', 'departamento', 'puesto', 'correo', 'telefono']
        # Solo incluir columnas que existen en el dataframe
        existing_columns = [col for col in column_order if col in df_combinado.columns]
        df_combinado = df_combinado[existing_columns]
        
        if progress_bar:
            progress_bar.progress(0.8, text="⚙️ Aplicando filtros...")
        
        # Aplicar filtros: excluir directores
        if 'puesto' in df_combinado.columns:
            df_combinado = df_combinado[~df_combinado['puesto'].apply(es_director)]
        
        if progress_bar:
            progress_bar.progress(1.0, text="✅ Procesamiento completado")
            time.sleep(0.5)  # Pequeña pausa para mostrar el 100%
        
        return df_combinado
        
    except Exception as e:
        st.error(f"❌ Error al procesar los datos: {str(e)}")
        import traceback
        st.error(f"Detalles del error: {traceback.format_exc()}")
        return None

def cargar_datos_desde_temporales():
    """Carga y procesa los datos desde los archivos temporales"""
    progress_bar = st.progress(0, text="📥 Cargando archivos temporales...")
    
    try:
        # Cargar archivos temporales
        progress_bar.progress(0.2, text="📁 Cargando archivo de ubicación...")
        ruta_ubicacion = cargar_archivo_temporal('ubicacion')
        df_ubicacion = cargar_archivo_desde_ruta(ruta_ubicacion, 1) if ruta_ubicacion else None
        
        progress_bar.progress(0.4, text="📁 Cargando archivo de correo...")
        ruta_correo = cargar_archivo_temporal('correo')
        df_correo = cargar_archivo_desde_ruta(ruta_correo, 0) if ruta_correo else None
        
        progress_bar.progress(0.6, text="📁 Cargando archivo de teléfono...")
        ruta_telefono = cargar_archivo_temporal('telefono')
        df_telefono = cargar_archivo_desde_ruta(ruta_telefono, 0) if ruta_telefono else None
        
        if df_ubicacion is not None and df_correo is not None and df_telefono is not None:
            # Procesar los datos
            df_combinado = procesar_datos(df_ubicacion, df_correo, df_telefono, progress_bar)
            if df_combinado is not None:
                # Obtener nombres de archivos
                nombre_ubicacion = os.path.basename(ruta_ubicacion).replace('ubicacion_', '')
                nombre_correo = os.path.basename(ruta_correo).replace('correo_', '')
                nombre_telefono = os.path.basename(ruta_telefono).replace('telefono_', '')
                
                # Guardar información del origen de los datos
                info_origen = {
                    'origen_ubicacion': f"Archivo: {nombre_ubicacion}",
                    'origen_correo': f"Archivo: {nombre_correo}",
                    'origen_telefono': f"Archivo: {nombre_telefono}",
                    'fecha_actualizacion': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                return df_combinado, info_origen
        return None, None
        
    finally:
        # Limpiar la barra de progreso
        time.sleep(0.5)
        progress_bar.empty()

def verificar_password_admin():
    """Verifica la contraseña para acceder a funciones de administrador"""
    if 'password_admin_verified' not in st.session_state:
        st.session_state.password_admin_verified = False
    
    if not st.session_state.password_admin_verified:
        st.write("### Directorio")
        col1, col2 = st.columns([2, 1])
        with col1:
            password = st.text_input("Contraseña de administrador:", type="password", key="admin_password_input")
        with col2:
            if st.button("🔓 Acceder", key="admin_access_btn"):
                if password == PASSWORD:
                    st.session_state.password_admin_verified = True
                    st.success("✅ Contraseña correcta")
                    st.rerun()
                else:
                    st.error("❌ Contraseña incorrecta")
    
    return st.session_state.password_admin_verified

def mostrar_panel_administrador():
    """Muestra el panel completo de administrador (solo con contraseña)"""
    if verificar_password_admin():
        # Botón para cerrar sesión de administrador
        if st.button("🚪 Cerrar Sesión de Administrador", key="close_admin_btn"):
            st.session_state.password_admin_verified = False
            st.success("✅ Sesión de administrador cerrada")
            st.rerun()
        
        # Sección para cargar archivos
        with st.expander("📁 Cargar archivos locales", expanded=False):
            st.info("Los archivos se guardarán temporalmente y se cargarán automáticamente al reiniciar la app")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                archivo_ubicacion = st.file_uploader(
                    "Archivo de Ubicación (Excel)",
                    type=['xlsx', 'xls'],
                    key="upload_ubicacion_admin",
                    help="Encabezados en la fila 2. Debe contener: Nombre, Puesto, Departamento"
                )
                if archivo_ubicacion:
                    guardar_archivo_temporal(archivo_ubicacion, 'ubicacion')
                    st.success(f"📄 {archivo_ubicacion.name} guardado")
            
            with col2:
                archivo_correo = st.file_uploader(
                    "Archivo de Correo (Excel)",
                    type=['xlsx', 'xls'],
                    key="upload_correo_admin",
                    help="Encabezados en la fila 1. Debe contener: Nombre, Correo"
                )
                if archivo_correo:
                    guardar_archivo_temporal(archivo_correo, 'correo')
                    st.success(f"📄 {archivo_correo.name} guardado")
                    
            with col3:
                archivo_telefono = st.file_uploader(
                    "Archivo de Teléfono (Excel)",
                    type=['xlsx', 'xls'],
                    key="upload_telefono_admin",
                    help="Encabezados en la fila 1. Debe contener: Nombre, Teléfono"
                )
                if archivo_telefono:
                    guardar_archivo_temporal(archivo_telefono, 'telefono')
                    st.success(f"📄 {archivo_telefono.name} guardado")
        
        # Botones de administración
        archivos_listos = archivos_temporales_existen()
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🚀 Procesar Archivos", type="primary", use_container_width=True, disabled=not archivos_listos, key="process_admin_btn"):
                df_combinado, info_origen = cargar_datos_desde_temporales()
                
                if df_combinado is not None:
                    st.session_state.df_combinado = df_combinado
                    st.session_state.info_origen = info_origen
                    st.session_state.datos_cargados = True
                    st.success("✅ Datos procesados correctamente")
                    st.rerun()
                else:
                    st.session_state.error_carga = "Error al procesar los archivos"
        
        with col2:
            if st.button("🗑️ Limpiar Archivos Temporales", use_container_width=True, key="clear_admin_btn"):
                limpiar_archivos_temporales()
                st.session_state.datos_cargados = False
                st.session_state.df_combinado = None
                st.session_state.info_origen = None
                st.session_state.password_admin_verified = False
                st.success("✅ Archivos temporales eliminados")
                st.rerun()
        
        # Información de archivos cargados
        if st.session_state.info_origen:
            with st.expander("📋 Información de archivos cargados", expanded=False):
                st.write(f"**Ubicación:** {st.session_state.info_origen['origen_ubicacion']}")
                st.write(f"**Correo:** {st.session_state.info_origen['origen_correo']}")
                st.write(f"**Teléfono:** {st.session_state.info_origen['origen_telefono']}")
                st.write(f"**Última actualización:** {st.session_state.info_origen['fecha_actualizacion']}")
        
        return True
    return False

def mostrar_seccion_administrador_datos():
    """Muestra la sección de administrador en los tabs (empleados no encontrados)"""
    if 'password_admin_verified' not in st.session_state:
        st.session_state.password_admin_verified = False
    
    if not st.session_state.password_admin_verified:
        st.write("### 👨‍💼 Administrador")
        col1, col2 = st.columns([2, 1])
        with col1:
            password = st.text_input("Contraseña de administrador:", type="password", key="admin_tab_password")
        with col2:
            if st.button("🔓 Acceder", key="admin_tab_btn"):
                if password == PASSWORD:
                    st.session_state.password_admin_verified = True
                    st.success("✅ Contraseña correcta")
                    st.rerun()
                else:
                    st.error("❌ Contraseña incorrecta")
        return False
    
    # Botón para cerrar sesión
    if st.button("🚪 Cerrar Sesión", key="close_admin_tab_btn"):
        st.session_state.password_admin_verified = False
        st.success("✅ Sesión de administrador cerrada")
        st.rerun()
    
    # Si la contraseña es correcta, mostrar los datos de empleados no encontrados
    # Necesitamos recrear los datos de no encontrados ya que ya no tenemos la columna en_ubicacion
    if st.session_state.datos_cargados and st.session_state.info_origen:
        # Cargar archivos originales para comparar
        ruta_ubicacion = cargar_archivo_temporal('ubicacion')
        ruta_correo = cargar_archivo_temporal('correo')
        ruta_telefono = cargar_archivo_temporal('telefono')
        
        if ruta_ubicacion and ruta_correo and ruta_telefono:
            df_ubicacion = cargar_archivo_desde_ruta(ruta_ubicacion, 1)
            df_correo = cargar_archivo_desde_ruta(ruta_correo, 0)
            df_telefono = cargar_archivo_desde_ruta(ruta_telefono, 0)
            
            if df_ubicacion is not None and df_correo is not None and df_telefono is not None:
                # Encontrar columnas de nombre
                col_nombre_ubi = encontrar_columna_clave(df_ubicacion, ['nombre', 'name', 'nombres'])
                col_nombre_correo = encontrar_columna_clave(df_correo, ['nombre', 'name', 'nombres'])
                col_nombre_telefono = encontrar_columna_clave(df_telefono, ['nombre', 'name', 'nombres'])
                
                if col_nombre_ubi and col_nombre_correo and col_nombre_telefono:
                    # Limpiar nombres
                    nombres_ubicacion = set(df_ubicacion[col_nombre_ubi].astype(str).str.strip().str.upper())
                    nombres_correo = set(df_correo[col_nombre_correo].astype(str).str.strip().str.upper())
                    nombres_telefono = set(df_telefono[col_nombre_telefono].astype(str).str.strip().str.upper())
                    
                    # Encontrar empleados que tienen correo/teléfono pero NO están en ubicación
                    nombres_con_contacto = nombres_correo.union(nombres_telefono)
                    nombres_no_en_ubicacion = nombres_con_contacto - nombres_ubicacion
                    
                    if len(nombres_no_en_ubicacion) > 0:
                        st.info(f"📋 Empleados con contacto pero no encontrados en ubicación: {len(nombres_no_en_ubicacion)}")
                        
                        # Crear dataframe con información básica
                        datos_no_encontrados = []
                        for nombre in nombres_no_en_ubicacion:
                            datos_no_encontrados.append({
                                'nombre': nombre,
                                'estado': 'No encontrado en ubicación'
                            })
                        
                        df_no_encontrados = pd.DataFrame(datos_no_encontrados)
                        st.dataframe(df_no_encontrados, use_container_width=True)
                        
                        # Exportar no encontrados
                        csv_no_encontrados = df_no_encontrados.to_csv(index=False, encoding='utf-8-sig')
                        st.download_button(
                            label="📥 Exportar No Encontrados (CSV)",
                            data=csv_no_encontrados,
                            file_name=f"empleados_no_encontrados_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                            mime="text/csv",
                            key="export_no_encontrados_admin"
                        )
                    else:
                        st.info("¡Todos los empleados con contacto están en la ubicación!")
    
    return True

def mostrar_sdu():
    """Muestra la interfaz del Sistema de Ubicación"""
    
    # Inicializar estado de sesión
    if 'datos_cargados' not in st.session_state:
        st.session_state.datos_cargados = False
    if 'df_combinado' not in st.session_state:
        st.session_state.df_combinado = None
    if 'info_origen' not in st.session_state:
        st.session_state.info_origen = None
    if 'error_carga' not in st.session_state:
        st.session_state.error_carga = None
    
    # Contenedor principal más compacto
    with st.container():
        # Mostrar panel de administrador (solo con contraseña)
        mostrar_panel_administrador()
        
        # Cargar automáticamente si existen archivos temporales pero no hay datos procesados
        if (not st.session_state.datos_cargados and archivos_temporales_existen()):
            df_combinado, info_origen = cargar_datos_desde_temporales()
            
            if df_combinado is not None:
                st.session_state.df_combinado = df_combinado
                st.session_state.info_origen = info_origen
                st.session_state.datos_cargados = True
        
        # Mostrar datos si están cargados
        if st.session_state.datos_cargados and st.session_state.df_combinado is not None:
            df_combinado = st.session_state.df_combinado
            
            # Buscador compacto - SOLO MUESTRA EMPLEADOS EN UBICACIÓN
            termino_busqueda = st.text_input(
                "🔎 Buscar empleado por nombre",
                placeholder="Ej: JUAN PEREZ",
                key="busqueda_input"
            )
            
            # Mostrar resultados de búsqueda si existe término
            if termino_busqueda:
                termino = termino_busqueda.upper().strip()
                df = df_combinado.copy()
                
                # Buscar en todas las columnas de texto
                resultados = df[df.astype(str).apply(lambda x: x.str.contains(termino, case=False).any(), axis=1)]
                
                if len(resultados) > 0:
                    st.success(f"✅ Encontrados {len(resultados)} empleados para: '{termino}'")
                    st.dataframe(resultados, use_container_width=True)
                    
                    # Exportar resultados de búsqueda
                    csv_busqueda = resultados.to_csv(index=False, encoding='utf-8-sig')
                    st.download_button(
                        label="📥 Exportar Resultados de Búsqueda",
                        data=csv_busqueda,
                        file_name=f"busqueda_{termino}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv",
                        key="export_busqueda"
                    )
                else:
                    st.warning(f"❌ No se encontraron empleados con: '{termino}'")
            else:
                # Mostrar todos los empleados en ubicación si no hay búsqueda
                st.dataframe(df_combinado, use_container_width=True)
                
                # Exportar todos los datos
                csv_data = df_combinado.to_csv(index=False, encoding='utf-8-sig')
                st.download_button(
                    label="📥 Exportar Todos los Datos (CSV)",
                    data=csv_data,
                    file_name=f"empleados_ubicacion_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    key="export_todos"
                )
            
            # Pestaña de administrador para ver empleados no encontrados
            st.markdown("---")
            with st.expander("👨‍💼 Panel de Administrador"):
                mostrar_seccion_administrador_datos()
        
        # Mostrar mensaje de error si existe
        if st.session_state.error_carga:
            st.error(f"❌ {st.session_state.error_carga}")
        
        # Mostrar estado actual
        if archivos_temporales_existen() and not st.session_state.datos_cargados:
            st.info("📊 Archivos temporales encontrados. Ingresa como administrador para procesarlos.")
        elif not archivos_temporales_existen():
            st.info("📝 Ingresa como administrador para subir archivos")

# Ejecutar la aplicación
if __name__ == "__main__":
    mostrar_sdu()