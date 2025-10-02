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
            
            # Buscador SIMPLE pero EFECTIVO
            termino_busqueda = st.text_input(
                "🔎 Buscar empleado por nombre",
                placeholder="Ej: OMAR REYES (busca cualquier coincidencia en el nombre)",
                key="busqueda_input"
            )
            
            # Mostrar resultados de búsqueda si existe término
            if termino_busqueda:
                # Usar la función de búsqueda SIMPLE
                resultados = buscar_empleados_simple(df_combinado, termino_busqueda)
                
                if len(resultados) > 0:
                    st.success(f"✅ Encontrados {len(resultados)} empleados para: '{termino_busqueda}'")
                    
                    # Crear tabla HTML con botones
                    html_table = """
                    <style>
                    .table-container {
                        width: 100%;
                        border-collapse: collapse;
                        margin: 10px 0;
                    }
                    .table-container th, .table-container td {
                        border: 1px solid #ddd;
                        padding: 8px;
                        text-align: left;
                    }
                    .table-container th {
                        background-color: #f2f2f2;
                        font-weight: bold;
                    }
                    .table-container tr:nth-child(even) {
                        background-color: #f9f9f9;
                    }
                    .whatsapp-btn {
                        background-color: #25D366;
                        color: white;
                        padding: 5px 10px;
                        border-radius: 4px;
                        text-decoration: none;
                        font-weight: bold;
                        display: inline-block;
                    }
                    .email-btn {
                        background-color: #EA4335;
                        color: white;
                        padding: 5px 10px;
                        border-radius: 4px;
                        text-decoration: none;
                        font-weight: bold;
                        display: inline-block;
                    }
                    .disabled-btn {
                        background-color: #cccccc;
                        color: #666666;
                        padding: 5px 10px;
                        border-radius: 4px;
                        text-decoration: none;
                        font-weight: bold;
                        display: inline-block;
                    }
                    </style>
                    <table class="table-container">
                        <thead>
                            <tr>
                                <th>Nombre</th>
                                <th>Departamento</th>
                                <th>Puesto</th>
                                <th>Acciones</th>
                            </tr>
                        </thead>
                        <tbody>
                    """
                    
                    for _, row in resultados.iterrows():
                        nombre = row['nombre']
                        departamento = row.get('departamento', '')
                        puesto = row.get('puesto', '')
                        telefono = row.get('telefono', '')
                        correo = row.get('correo', '')
                        
                        # Crear botones
                        whatsapp_url = crear_url_whatsapp(telefono) if telefono and telefono != '' else None
                        correo_url = crear_url_correo(correo) if correo and correo != '' else None
                        
                        acciones_html = ""
                        
                        if whatsapp_url:
                            acciones_html += f'<a href="{whatsapp_url}" target="_blank" class="whatsapp-btn">📱 WhatsApp</a> '
                        else:
                            acciones_html += '<span class="disabled-btn">📱 Sin teléfono</span> '
                            
                        if correo_url:
                            acciones_html += f'<a href="{correo_url}" target="_blank" class="email-btn">📧 Correo</a>'
                        else:
                            acciones_html += '<span class="disabled-btn">📧 Sin correo</span>'
                        
                        html_table += f"""
                            <tr>
                                <td>{nombre}</td>
                                <td>{departamento}</td>
                                <td>{puesto}</td>
                                <td>{acciones_html}</td>
                            </tr>
                        """
                    
                    html_table += """
                        </tbody>
                    </table>
                    """
                    
                    # Mostrar la tabla HTML
                    st.markdown(html_table, unsafe_allow_html=True)
                    
                    # Exportar resultados de búsqueda
                    csv_busqueda = resultados.to_csv(index=False, encoding='utf-8-sig')
                    st.download_button(
                        label="📥 Exportar Resultados de Búsqueda",
                        data=csv_busqueda,
                        file_name=f"busqueda_{termino_busqueda}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv",
                        key="export_busqueda"
                    )
                else:
                    st.warning(f"❌ No se encontraron empleados con: '{termino_busqueda}'")
                    
            else:
                # Mostrar todos los empleados en ubicación si no hay búsqueda
                # Crear tabla HTML con botones para todos los datos
                html_table = """
                <style>
                .table-container {
                    width: 100%;
                    border-collapse: collapse;
                    margin: 10px 0;
                }
                .table-container th, .table-container td {
                    border: 1px solid #ddd;
                    padding: 8px;
                    text-align: left;
                }
                .table-container th {
                    background-color: #f2f2f2;
                    font-weight: bold;
                }
                .table-container tr:nth-child(even) {
                    background-color: #f9f9f9;
                }
                .whatsapp-btn {
                    background-color: #25D366;
                    color: white;
                    padding: 5px 10px;
                    border-radius: 4px;
                    text-decoration: none;
                    font-weight: bold;
                    display: inline-block;
                }
                .email-btn {
                    background-color: #EA4335;
                    color: white;
                    padding: 5px 10px;
                    border-radius: 4px;
                    text-decoration: none;
                    font-weight: bold;
                    display: inline-block;
                }
                .disabled-btn {
                    background-color: #cccccc;
                    color: #666666;
                    padding: 5px 10px;
                    border-radius: 4px;
                    text-decoration: none;
                    font-weight: bold;
                    display: inline-block;
                }
                </style>
                <table class="table-container">
                    <thead>
                        <tr>
                            <th>Nombre</th>
                            <th>Departamento</th>
                            <th>Puesto</th>
                            <th>Acciones</th>
                        </tr>
                    </thead>
                    <tbody>
                """
                
                for _, row in df_combinado.iterrows():
                    nombre = row['nombre']
                    departamento = row.get('departamento', '')
                    puesto = row.get('puesto', '')
                    telefono = row.get('telefono', '')
                    correo = row.get('correo', '')
                    
                    # Crear botones
                    whatsapp_url = crear_url_whatsapp(telefono) if telefono and telefono != '' else None
                    correo_url = crear_url_correo(correo) if correo and correo != '' else None
                    
                    acciones_html = ""
                    
                    if whatsapp_url:
                        acciones_html += f'<a href="{whatsapp_url}" target="_blank" class="whatsapp-btn">📱 WhatsApp</a> '
                    else:
                        acciones_html += '<span class="disabled-btn">📱 Sin teléfono</span> '
                        
                    if correo_url:
                        acciones_html += f'<a href="{correo_url}" target="_blank" class="email-btn">📧 Correo</a>'
                    else:
                        acciones_html += '<span class="disabled-btn">📧 Sin correo</span>'
                    
                    html_table += f"""
                        <tr>
                            <td>{nombre}</td>
                            <td>{departamento}</td>
                            <td>{puesto}</td>
                            <td>{acciones_html}</td>
                        </tr>
                    """
                
                html_table += """
                    </tbody>
                </table>
                """
                
                # Mostrar la tabla HTML
                st.markdown(html_table, unsafe_allow_html=True)
                
                # Exportar todos los datos
                csv_data = df_combinado.to_csv(index=False, encoding='utf-8-sig')
                st.download_button(
                    label="📥 Exportar Todos los Datos (CSV)",
                    data=csv_data,
                    file_name=f"empleados_ubicacion_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    key="export_todos"
                )
        
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