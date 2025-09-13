import streamlit as st
import pandas as pd
from datetime import datetime
import os
import re
import tempfile

def cargar_archivo_local(uploaded_file, header_row=0):
    """Carga un archivo Excel desde el sistema local usando archivos temporales seguros"""
    try:
        if uploaded_file is not None:
            # Crear un archivo temporal seguro
            with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp_file:
                tmp_file.write(uploaded_file.getbuffer())
                temp_path = tmp_file.name
            
            try:
                # Leer el archivo Excel
                df = pd.read_excel(temp_path, header=header_row, engine='openpyxl')
                
                # Limpiar nombres de columnas
                df.columns = df.columns.astype(str).str.strip().str.lower().str.replace(' ', '_')
                df.columns = df.columns.str.replace(r'[^\w_]', '', regex=True)
                
                # Eliminar filas completamente vacías
                df = df.dropna(how='all')
                
                return df
                
            finally:
                # Asegurarse de eliminar el archivo temporal
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                    
        return None
    except Exception as e:
        st.error(f"❌ Error al cargar el archivo: {str(e)}")
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
        
        # Mostrar solo el resumen final
        st.success(f"📊 Procesamiento completado: {encontrados}/{total} registros encontrados en ubicación")
        
        return df_relacion_clean
        
    except Exception as e:
        st.error(f"❌ Error al procesar los datos: {str(e)}")
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
    
    # Carga de archivos
    st.markdown("---")
    st.subheader("📁 Cargar Archivos Excel")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Archivo de Ubicación")
        uploaded_file_ubicacion = st.file_uploader(
            "Seleccione el archivo de Ubicación", 
            type=['xlsx', 'xls'],
            key="ubicacion_upload"
        )
        
    with col2:
        st.markdown("### Archivo de Relación")
        uploaded_file_relacion = st.file_uploader(
            "Seleccione el archivo de Relación", 
            type=['xlsx', 'xls'],
            key="relacion_upload"
        )
    
    # Botón para procesar datos
    if uploaded_file_ubicacion is not None and uploaded_file_relacion is not None:
        if st.button("🔄 Procesar Datos", type="primary", use_container_width=True):
            with st.spinner("Procesando datos..."):
                # Cargar los archivos con configuración fija
                df_ubicacion = cargar_archivo_local(uploaded_file_ubicacion, 1)  # Fila 2 (índice 1)
                df_relacion = cargar_archivo_local(uploaded_file_relacion, 0)    # Fila 1 (índice 0)
                
                if df_ubicacion is not None and df_relacion is not None:
                    # Procesar los datos
                    df_combinado = procesar_datos(df_ubicacion, df_relacion)
                    
                    if df_combinado is not None:
                        st.session_state.df_combinado = df_combinado
                        st.session_state.datos_cargados = True
    
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
        
        # Pestañas para mostrar resultados
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
        
        # Búsqueda
        st.markdown("---")
        st.subheader("🔎 Búsqueda de Empleados")
        
        termino_busqueda = st.text_input(
            "Buscar empleado por nombre",
            placeholder="Ej: JUAN PEREZ",
            key="busqueda_input"
        )
        
        if st.button("🔍 Buscar Empleado", key="btn_buscar", use_container_width=True):
            if termino_busqueda:
                termino = termino_busqueda.upper().strip()
                df = st.session_state.df_combinado.copy()
                
                # Buscar en todas las columnas de texto
                resultados = df[df.astype(str).apply(lambda x: x.str.contains(termino, case=False).any(), axis=1)]
                
                if len(resultados) > 0:
                    st.success(f"✅ Encontrados {len(resultados)} empleados")
                    st.dataframe(resultados)
                else:
                    st.warning(f"❌ No se encontraron empleados con: '{termino}'")
            else:
                st.warning("Por favor ingrese un nombre para buscar")
        
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
        st.info("ℹ️ Cargue ambos archivos Excel y haga clic en 'Procesar Datos' para comenzar")

    # Información de ayuda
    with st.expander("ℹ️ Instrucciones de uso"):
        st.markdown("""
        **Cómo usar el sistema:**
        1. **Cargar archivos:** 
           - 📁 **Ubicación**: Archivo con encabezados en fila 2
           - 📁 **Relación**: Archivo con encabezados en fila 1
        2. **Procesar:** Haga clic en "Procesar Datos" para verificar empleados
        3. **Resultados:** Vea empleados encontrados y no encontrados
        4. **Buscar:** Use el buscador para encontrar empleados específicos
        5. **Exportar:** Descargue los resultados en formato CSV
        
        **Nota:** El sistema solo usa el archivo de Ubicación para verificar existencia, 
        pero muestra toda la información del archivo de Relación.
        """)