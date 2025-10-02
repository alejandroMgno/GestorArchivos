🔍 Sistema de Ubicación de Contactos de Empleados
Una aplicación web desarrollada con Streamlit para buscar y contactar empleados de manera eficiente, integrando información de ubicación, correos electrónicos y números de teléfono.

✨ Características Principales
🔎 Búsqueda Avanzada
Búsqueda por nombre: Encuentra empleados rápidamente usando cualquier parte del nombre

Filtros automáticos: Excluye automáticamente a directores (no subdirectores)

Resultados en tiempo real: Búsqueda instantánea mientras escribes

📱 Contacto Directo
Integración con WhatsApp: Contacta directamente vía WhatsApp con formato internacional (+52)

Envío de correos: Abre tu cliente de correo con el destinatario predefinido

Selección intuitiva: Interfaz de selección con información completa del contacto

🛡️ Panel de Administración
Gestión segura: Acceso protegido con contraseña

Carga de archivos: Sube y procesa archivos Excel con datos de empleados

Almacenamiento temporal: Los archivos se mantienen entre sesiones

Procesamiento por lotes: Combina automáticamente datos de múltiples fuentes

📊 Estructura de Archivos Requeridos
La aplicación requiere tres archivos Excel:

1. 📍 Archivo de Ubicación
Encabezados en fila 2

Columnas requeridas:

Nombre (o similar): Nombres de los empleados

Puesto (opcional): Cargos o posiciones

Departamento (opcional): Áreas o departamentos

2. 📧 Archivo de Correo
Encabezados en fila 1

Columnas requeridas:

Nombre (o similar): Nombres de los empleados

Correo (o similar): Direcciones de email

3. 📞 Archivo de Teléfono
Encabezados en fila 1

Columnas requeridas:

Nombre (o similar): Nombres de los empleados

Teléfono (o similar): Números de contacto

🚀 Instalación y Uso
Prerrequisitos
bash
Python 3.8+
pip install streamlit pandas requests openpyxl
Ejecución
bash
streamlit run app.py
📋 Pasos de Uso
Acceso como Administrador:

Haz clic en "Panel de Administrador"

Ingresa la contraseña: admin2021*+

Carga de Archivos:

Sube los tres archivos Excel requeridos

Los archivos se guardan automáticamente

Procesamiento:

Haz clic en "Procesar Archivos"

Los datos se combinan y filtran automáticamente

Búsqueda y Contacto:

Usa la barra de búsqueda para encontrar empleados

Selecciona un contacto de la lista

Usa los botones de WhatsApp o Correo para contactar

🎯 Funcionalidades de Búsqueda
Búsqueda parcial: Encuentra coincidencias con cualquier parte del nombre

Búsqueda múltiple: Separa términos con espacios para búsquedas más específicas

Filtrado inteligente: Solo muestra empleados con información de contacto válida

🔒 Seguridad y Privacidad
Contraseña de administrador: Protege el acceso a funciones críticas

Datos temporales: Los archivos se almacenan localmente

Filtrado de información: Solo se muestran empleados con datos de contacto

📈 Exportación de Datos
Exportar resultados de búsqueda: Descarga CSV con los empleados encontrados

Exportar todos los datos: Descarga completa de la base de contactos

🛠️ Estructura del Proyecto
text
sistema-ubicacion-contactos/
├── app.py                 # Aplicación principal
├── temp_archivos/         # Directorio temporal para archivos
├── README.md             # Este archivo
└── requirements.txt      # Dependencias del proyecto
⚙️ Configuración Técnica
Dependencias Principales
streamlit: Interfaz web

pandas: Procesamiento de datos

requests: Manejo de sesiones HTTP

openpyxl: Lectura de archivos Excel

Características de Rendimiento
Carga progresiva: Barra de progreso durante el procesamiento

Sesiones persistentes: Mantiene el estado entre interacciones

Manejo de errores: Validación robusta de archivos y datos

🆘 Solución de Problemas
Problemas Comunes
Error al cargar archivos:

Verifica que los encabezados estén en la fila correcta

Confirma que los nombres de columnas sean similares a los esperados

No se encuentran empleados:

Revisa que los nombres coincidan entre los tres archivos

Verifica que los empleados tengan al menos teléfono o correo

Problemas de contraseña:

La contraseña por defecto es: admin2021*+

📞 Soporte
Para reportar problemas o sugerir mejoras, contacta al equipo de desarrollo.

Versión: 1.0
Última actualización: Diciembre 2024
Desarrollado con 🐍 Python y ❤️