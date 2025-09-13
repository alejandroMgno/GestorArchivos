import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import os
import re
import tempfile
from io import BytesIO
from urllib.parse import urlparse, unquote, parse_qs
import urllib3
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

# Desactivar warnings de SSL para desarrollo
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

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

def decode_onedrive_url(short_url):
    """Decodifica una URL corta de OneDrive (1drv.ms) a URL directa"""
    try:
        session = create_session()
        response = session.head(short_url, allow_redirects=True, timeout=10, verify=False)
        final_url = response.url
        
        # Para URLs de OneDrive personal, convertirlas a URL de descarga
        if 'sharepoint.com' in final_url or 'onedrive.live.com' in final_url:
            if '?download=1' not in final_url:
                if '?' in final_url:
                    final_url = final_url + '&download=1'
                else:
                    final_url = final_url + '?download=1'
        
        return final_url
        
    except Exception as e:
        st.error(f"❌ Error al decodificar URL: {str(e)}")
        return short_url

def descargar_archivo_desde_onedrive(url_onedrive):
    """Descarga un archivo desde OneDrive personal"""
    try:
        # Decodificar la URL corta
        download_url = decode_onedrive_url(url_onedrive)
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        }
        
        session = create_session()
        response = session.get(download_url, headers=headers, timeout=30, verify=False)
        
        if response.status_code == 200:
            # Verificar que es un archivo Excel
            if len(response.content) > 1000 and response.content[:4] == b'PK\x03\x04':
                return BytesIO(response.content)
            else:
                st.error("❌ El archivo descargado no es un Excel válido")
                return None
        else:
            st.error(f"❌ Error HTTP {response.status_code} al descargar archivo")
            return None
            
    except Exception as e:
        st.error(f"❌ Error al descargar desde OneDrive: {str(e)}")
        return None

def cargar_archivo(origen, header_row=0):
    """Carga un archivo desde URL de OneDrive o archivo subido"""
    try:
        if isinstance(origen, str) and origen.startswith(('http://', 'https://')):
            # Es una URL de OneDrive
            with st.spinner(f"🌐 Descargando archivo desde OneDrive..."):
                file_content = descargar_archivo_desde_onedrive(origen)
                if file_content:
                    df = pd.read_excel(file_content, header=header_row, engine='openpyxl')
                    return df
                else:
                    return None
        else:
            # Es un archivo subido
            return cargar_archivo_local(origen, header_row)
        
    except Exception as e:
        st.error(f"❌ Error al cargar el archivo: {str(e)}")
        return None

def cargar_archivo_local(uploaded_file, header_row=0):
    """Carga un archivo Excel desde el sistema local"""
    try:
        if uploaded_file is not None:
            # Leer directamente desde el archivo subido
            df = pd.read_excel(uploaded_file, header=header_row, engine='openpyxl')
            
            # Limpiar nombres de columnas
            df.columns = df.columns.astype(str).str.strip().str.lower().str.replace(' ', '_')
            df.columns = df.columns.str.replace(r'[^\w_]', '', regex=True)
            
            # Eliminar filas completamente vacías
            df = df.dropna(how='all')
            
            return df
                    
        return None
    except Exception as e:
        st.error(f"❌ Error al cargar el archivo local: {str(e)}")
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

def procesar_datos(df_ubicacion, df_relacion):
    """Procesa y combina los datos de ambos archivos"""
    try:
        if df_ubicacion is None or df_relacion is None:
            return None
        
        # Listas de posibles nombres para cada campo
        posibles_nombres_nombre = ['nombre', 'name', 'nombres', 'empleado', 'colaborador']
        
        # Encontrar columnas clave
        col_nombre_ubi = encontrar_columna_clave(df_ubicacion, posibles_nombres_nombre)
        col_nombre_rel = encontrar_columna_clave(df_relacion, posibles_nombres_nombre)
        
        # Validar columnas
        if not col_nombre_ubi:
            st.error("❌ No se encontró columna de 'nombre' en el archivo de ubicación")
            return None
        
        if not col_nombre_rel:
            st.error("❌ No se encontró columna de 'nombre' en el archivo de relación")
            return None
        
        # Limpiar y estandarizar datos
        df_ubicacion_clean = df_ubicacion.copy()
        df_relacion_clean = df_relacion.copy()
        
        # Limpiar columna de nombre en ambos archivos
        df_ubicacion_clean[col_nombre_ubi] = df_ubicacion_clean[col_nombre_ubi].astype(str).str.strip().str.upper()
        df_relacion_clean[col_nombre_rel] = df_relacion_clean[col_nombre_rel].astype(str).str.strip().str.upper()
        
        # Eliminar valores inválidos
        df_ubicacion_clean = df_ubicacion_clean[df_ubicacion_clean[col_nombre_ubi] != 'NAN']
        df_ubicacion_clean = df_ubicacion_clean[df_ubicacion_clean[col_nombre_ubi] != 'NONE']
        df_ubicacion_clean = df_ubicacion_clean[~df_ubicacion_clean[col_nombre_ubi].isna()]
        df_ubicacion_clean = df_ubicacion_clean[df_ubicacion_clean[col_nombre_ubi] != '']
        
        df_relacion_clean = df_relacion_clean[df_relacion_clean[col_nombre_rel] != 'NAN']
        df_relacion_clean = df_relacion_clean[df_relacion_clean[col_nombre_rel] != 'NONE']
        df_relacion_clean = df_relacion_clean[~df_relacion_clean[col_nombre_rel].isna()]
        df_relacion_clean = df_relacion_clean[df_relacion_clean[col_nombre_rel] != '']
        
        # Verificar existencia en ubicación
        nombres_ubicacion = set(df_ubicacion_clean[col_nombre_ubi].dropna().unique())
        
        # Agregar columna de verificación al dataframe de relación
        df_relacion_clean['en_ubicacion'] = df_relacion_clean[col_nombre_rel].isin(nombres_ubicacion)
        
        # Estadísticas
        total = len(df_relacion_clean)
        encontrados = sum(df_relacion_clean['en_ubicacion'])
        no_encontrados = total - encontrados
        
        st.success(f"✅ Procesamiento completado: {encontrados}/{total} registros encontrados en ubicación")
        
        return df_relacion_clean
        
    except Exception as e:
        st.error(f"❌ Error al procesar los datos: {str(e)}")
        import traceback
        st.error(f"Detalles del error: {traceback.format_exc()}")
        return None

def mostrar_sdu():
    """Muestra la interfaz del Sistema de Ubicación"""
    st.title("🔍 SDU - Sistema de Ubicación")
    st.markdown("Sistema para verificar empleados en ubicación")
    
    # Inicializar estado de sesión
    if 'datos_cargados' not in st.session_state:
        st.session_state.datos_cargados = False
    if 'df_combinado' not in st.session_state:
        st.session_state.df_combinado = None
    
    # URLs predefinidas de OneDrive
    URL_UBICACION = "https://1drv.ms/x/c/88b10bb315761c17/EaMcP00dIK1Dn-ZSZfO9haABR71sEh8-_408ul6nYP7SNw?e=FG6bgm"
    URL_RELACION = "https://1drv.ms/x/c/88b10bb315761c17/EawEt81cpmtKrPEwLhCJkMsBOlOf9OL9eyRhWX5qiz3Q6g?e=KsJXQY"
    
    # Carga de archivos
    st.markdown("---")
    st.subheader("📁 Cargar Archivos desde OneDrive")
    
    # Información importante
    with st.expander("⚠️ Instrucciones importantes (Click para expandir)"):
        st.markdown("""
        **Para que funcione correctamente:**
        1. **Abrir cada archivo** en OneDrive web
        2. **Click en "Compartir"** 
        3. **Seleccionar** "Cualquier persona con el vínculo"
        4. **Configurar** como "Permitir edición"
        5. **Usar el nuevo enlace** generado
        
        **Si falla la descarga automática:**
        - Descarga manualmente los archivos
        - Súbelos usando la opción de archivos locales
        """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Archivo de Ubicación")
        st.info("Encabezados en fila 2")
        
        uso_url_ubicacion = st.checkbox("Usar URL predefinida para Ubicación", value=True, key="use_url_ubi")
        
        if uso_url_ubicacion:
            st.success("✅ Usando URL predefinida de Ubicación")
            st.code(URL_UBICACION, language="text")
            uploaded_file_ubicacion = URL_UBICACION
        else:
            opcion_ubicacion = st.radio(
                "Origen del archivo de Ubicación:",
                ["URL de OneDrive", "Subir archivo local"],
                key="opcion_ubi"
            )
            
            if opcion_ubicacion == "URL de OneDrive":
                uploaded_file_ubicacion = st.text_input(
                    "URL de OneDrive para Ubicación",
                    value="",
                    placeholder="https://1drv.ms/...",
                    key="url_ubicacion_input"
                )
            else:
                uploaded_file_ubicacion = st.file_uploader(
                    "Subir archivo de Ubicación",
                    type=['xlsx', 'xls'],
                    key="upload_ubicacion"
                )
        
    with col2:
        st.markdown("### Archivo de Relación")
        st.info("Encabezados en fila 1")
        
        uso_url_relacion = st.checkbox("Usar URL predefinida para Relación", value=True, key="use_url_rel")
        
        if uso_url_relacion:
            st.success("✅ Usando URL predefinida de Relación")
            st.code(URL_RELACION, language="text")
            uploaded_file_relacion = URL_RELACION
        else:
            opcion_relacion = st.radio(
                "Origen del archivo de Relación:",
                ["URL de OneDrive", "Subir archivo local"],
                key="opcion_rel"
            )
            
            if opcion_relacion == "URL de OneDrive":
                uploaded_file_relacion = st.text_input(
                    "URL de OneDrive para Relación",
                    value="",
                    placeholder="https://1drv.ms/...",
                    key="url_relacion_input"
                )
            else:
                uploaded_file_relacion = st.file_uploader(
                    "Subir archivo de Relación",
                    type=['xlsx', 'xls'],
                    key="upload_relacion"
                )
    
    # Botón para procesar datos
    tiene_ubicacion = uploaded_file_ubicacion and (uso_url_ubicacion or uploaded_file_ubicacion.startswith('http') or hasattr(uploaded_file_ubicacion, 'name'))
    tiene_relacion = uploaded_file_relacion and (uso_url_relacion or uploaded_file_relacion.startswith('http') or hasattr(uploaded_file_relacion, 'name'))
    
    if tiene_ubicacion and tiene_relacion:
        if st.button("🔄 Procesar Datos", type="primary", use_container_width=True):
            with st.spinner("Descargando y procesando datos..."):
                # Cargar los archivos con configuración fija
                df_ubicacion = cargar_archivo(uploaded_file_ubicacion, 1)  # Fila 2 (índice 1)
                df_relacion = cargar_archivo(uploaded_file_relacion, 0)    # Fila 1 (índice 0)
                
                if df_ubicacion is not None and df_relacion is not None:
                    # Procesar los datos
                    df_combinado = procesar_datos(df_ubicacion, df_relacion)
                    
                    if df_combinado is not None:
                        st.session_state.df_combinado = df_combinado
                        st.session_state.datos_cargados = True
                        st.success("✅ Datos procesados correctamente")
                else:
                    st.error("❌ No se pudieron cargar uno o ambos archivos. Verifica que:")
                    st.error("1. Los archivos estén compartidos correctamente")
                    st.error("2. Las URLs sean correctas")
                    st.error("3. Los archivos sean válidos (formato .xlsx)")
    
    # Mostrar datos si están cargados
    if st.session_state.datos_cargados and st.session_state.df_combinado is not None:
        st.markdown("---")
        st.subheader("📊 Resultados del Procesamiento")
        
        # Mostrar estadísticas
        col1, col2, col3 = st.columns(3)
        with col1:
            total_registros = len(st.session_state.df_combinado)
            st.metric("Total de registros", total_registros)
        with col2:
            encontrados = sum(st.session_state.df_combinado['en_ubicacion'])
            st.metric("En ubicación", encontrados)
        with col3:
            no_encontrados = total_registros - encontrados
            st.metric("No encontrados", no_encontrados)
        
        # Buscador integrado en la sección de resultados
        st.markdown("---")
        col_search1, col_search2 = st.columns([3, 1])
        with col_search1:
            termino_busqueda = st.text_input(
                "🔎 Buscar empleado por nombre",
                placeholder="Ej: JUAN PEREZ",
                key="busqueda_input"
            )
        with col_search2:
            st.write("")  # Espacio vertical
            if st.button("Buscar", key="btn_buscar", use_container_width=True):
                st.session_state.buscar_termino = termino_busqueda.upper().strip()
        
        # Mostrar resultados de búsqueda si existe término
        if hasattr(st.session_state, 'buscar_termino') and st.session_state.buscar_termino:
            termino = st.session_state.buscar_termino
            df = st.session_state.df_combinado.copy()
            
            # Buscar en todas las columnas de texto
            resultados = df[df.astype(str).apply(lambda x: x.str.contains(termino, case=False).any(), axis=1)]
            
            if len(resultados) > 0:
                st.success(f"✅ Encontrados {len(resultados)} empleados para: '{termino}'")
                
                # Mostrar resultados de búsqueda
                tab_busqueda1, tab_busqueda2 = st.tabs(["✅ Encontrados en búsqueda", "📋 Detalles de búsqueda"])
                
                with tab_busqueda1:
                    st.dataframe(resultados)
                
                with tab_busqueda2:
                    st.write("**Distribución de resultados de búsqueda:**")
                    encontrados_busqueda = sum(resultados['en_ubicacion'])
                    no_encontrados_busqueda = len(resultados) - encontrados_busqueda
                    
                    col_b1, col_b2 = st.columns(2)
                    with col_b1:
                        st.metric("En ubicación", encontrados_busqueda)
                    with col_b2:
                        st.metric("No en ubicación", no_encontrados_busqueda)
                    
                    # Exportar resultados de búsqueda
                    csv_data = resultados.to_csv(index=False, encoding='utf-8-sig')
                    st.download_button(
                        label="📥 Exportar Resultados de Búsqueda",
                        data=csv_data,
                        file_name=f"busqueda_{termino}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv",
                        key="export_busqueda"
                    )
            else:
                st.warning(f"❌ No se encontraron empleados con: '{termino}'")
        
        # Pestañas para mostrar todos los resultados
        st.markdown("---")
        tab1, tab2 = st.tabs(["✅ Empleados en Ubicación", "❌ Empleados No Encontrados"])
        
        with tab1:
            st.subheader("Empleados que SÍ están en Ubicación")
            df_encontrados = st.session_state.df_combinado[st.session_state.df_combinado['en_ubicacion'] == True]
            
            if len(df_encontrados) > 0:
                st.dataframe(df_encontrados)
                
                # Exportar encontrados
                csv_data = df_encontrados.to_csv(index=False, encoding='utf-8-sig')
                st.download_button(
                    label="📥 Exportar Encontrados (CSV)",
                    data=csv_data,
                    file_name=f"empleados_en_ubicacion_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    key="export_encontrados"
                )
            else:
                st.info("No se encontraron empleados en la ubicación")
        
        with tab2:
            st.subheader("Empleados que NO están en Ubicación")
            df_no_encontrados = st.session_state.df_combinado[st.session_state.df_combinado['en_ubicacion'] == False]
            
            if len(df_no_encontrados) > 0:
                st.dataframe(df_no_encontrados)
                
                # Exportar no encontrados
                csv_data = df_no_encontrados.to_csv(index=False, encoding='utf-8-sig')
                st.download_button(
                    label="📥 Exportar No Encontrados (CSV)",
                    data=csv_data,
                    file_name=f"empleados_no_encontrados_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    key="export_no_encontrados"
                )
            else:
                st.info("¡Todos los empleados están en la ubicación!")
        
        # Exportar todos los datos
        st.markdown("---")
        st.subheader("📋 Exportar Datos Completos")
        
        csv_data = st.session_state.df_combinado.to_csv(index=False, encoding='utf-8-sig')
        st.download_button(
            label="📥 Exportar Todos los Datos (CSV)",
            data=csv_data,
            file_name=f"todos_empleados_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            key="export_todos"
        )
        
    else:
        st.info("ℹ️ Configure los archivos y haga clic en 'Procesar Datos' para comenzar")

    # Información de ayuda
    with st.expander("ℹ️ Información del sistema"):
        st.markdown("""
        **Funcionalidades:**
        - ✅ Descarga automática desde OneDrive
        - ✅ Soporte para archivos locales
        - ✅ Búsqueda avanzada por nombre
        - ✅ Exportación a CSV
        - ✅ Separación de resultados (encontrados/no encontrados)
        
        **Configuración de encabezados:**
        - 📁 Ubicación: Encabezados en fila 2 (segunda fila)
        - 📁 Relación: Encabezados en fila 1 (primera fila)
        """)