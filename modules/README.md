📋 SDU - Sistema de Ubicación de Empleados
Sistema web para la verificación y gestión de ubicación de empleados, desarrollado con Streamlit y Python.

🚀 Características
🔐 Autenticación segura con múltiples niveles de usuario

🌐 Descarga automática desde OneDrive y SharePoint

🔍 Búsqueda avanzada por nombre, correo o teléfono

📤 Exportación de datos a formato CSV

📱 Interfaz responsive y fácil de usar

👥 Usuarios y Accesos
1. 👑 Administrador
Usuario: admin

Contraseña: admin123

Permisos: Acceso completo a todas las funcionalidades

2. 👥 Recursos Humanos
Usuario: rh

Contraseña: Rrhh2025*+

Permisos: Acceso completo al módulo SDU

3. 👤 Usuario General
Usuario: usuario

Contraseña: user123

Permisos: Acceso básico al sistema

📦 Instalación
Requisitos previos
Python 3.8+

pip (gestor de paquetes de Python)

Pasos de instalación
Clonar o descargar el proyecto

bash
git clone https://github.com/alejandroMgno/GestorArchivos
cd sistema-ubicacion
Instalar dependencias

bash
pip install -r requirements.txt
Ejecutar la aplicación

bash
streamlit run main_app.py
Acceder al sistema

Abrir navegador en: http://localhost:8501

Ingresar con las credenciales proporcionadas

🗂️ Estructura del Proyecto
text
sistema-ubicacion/
│
├── main_app.py              # Aplicación principal
├── requirements.txt         # Dependencias del proyecto
│
├── modules/
│   ├── __init__.py         # Inicializador del módulo
│   ├── auth.py             # Sistema de autenticación
│   └── sdu_module.py       # Módulo principal SDU
│
└── README.md               # Este archivo
📁 Configuración de Archivos
Archivos de entrada requeridos:
📋 Archivo de Ubicación

Encabezados en la segunda fila (fila 1)

Debe contener columnas: nombre, correo, telefono

Formato: Excel (.xlsx, .xls)

📊 Archivo de Relación

Encabezados en la primera fila (fila 0)

Debe contener columnas: nombre, correo, telefono

Formato: Excel (.xlsx, .xls)

Opciones de carga:
🌐 URLs de OneDrive/SharePoint (descarga automática)

📁 Archivos locales (upload manual)

🎯 Funcionalidades Principales
1. 🔍 Procesamiento de Datos
Carga automática desde múltiples fuentes

Validación y limpieza de datos

Detección automática de columnas

Combinación inteligente de datasets

2. 📊 Visualización de Resultados
Métricas en tiempo real: Total, Encontrados, No encontrados

Pestañas separadas: Empleados ubicados vs No ubicados

Búsqueda integrada: Filtrado por cualquier campo

Vista previa: Visualización de datos antes de exportar

3. 📤 Exportación de Datos
Formatos soportados: CSV (UTF-8)

Opciones de exportación:

📥 Resultados completos

📥 Solo empleados ubicados

📥 Solo empleados no ubicados

📥 Resultados de búsqueda específicos

4. 🌐 Integración con Cloud
OneDrive Personal: URLs 1drv.ms

SharePoint Empresarial: URLs sharepoint.com

Descarga automática con conversión de URLs

Soporte para autenticación (opcional)

🛠️ Tecnologías Utilizadas
Python 3.8+: Lenguaje principal

Streamlit: Framework web interactivo

Pandas: Procesamiento de datos

OpenPyXL: Manejo de archivos Excel

Requests: Cliente HTTP para descargas

Hashlib: Encriptación de contraseñas

⚙️ Configuración Avanzada
Variables de Entorno (Opcional)
python
# Para desarrollo, puedes crear un archivo .streamlit/secrets.toml
AZURE_CLIENT_ID = "tu_client_id"
AZURE_TENANT_ID = "tu_tenant_id" 
AZURE_CLIENT_SECRET = "tu_client_secret"
Personalización de Columnas
El sistema detecta automáticamente columnas con estos nombres:

Nombre: nombre, name, nombres, empleado, colaborador

Correo: correo, email, mail, e-mail, correo_electronico

Teléfono: tel, fono, telefono, phone, celular, cel, movil

🚦 Flujo de Trabajo
Login → Ingresar al sistema con credenciales válidas

Carga → Seleccionar archivos de Ubicación y Relación

Procesar → Ejecutar el análisis de datos

Analizar → Revisar resultados en el dashboard

Buscar → Filtrar información específica si es necesario

Exportar → Descargar resultados en CSV

🆘 Solución de Problemas
Error común: "File is not a zip file"
Solución: Verificar que los archivos estén compartidos como "Cualquier persona con el vínculo" en OneDrive/SharePoint

Error común: SSL Certificate verify failed
Solución: El sistema incluye manejo automático de errores SSL

Error común: No se encuentran columnas
Solución: Verificar que los archivos tengan las columnas requeridas

📞 Soporte
Para reportar issues o solicitar ayuda:

Verificar que se siguieron los pasos de instalación

Confirmar que los archivos de entrada tienen el formato correcto

Proporcionar capturas de pantalla del error

📄 Licencia
Este proyecto es de uso interno para la gestión de recursos humanos.

🔄 Versiones
v1.0 (2024): Versión inicial con funcionalidades básicas

v1.1 (2024): Integración con OneDrive/SharePoint

v1.2 (2024): Mejoras en interfaz y exportación