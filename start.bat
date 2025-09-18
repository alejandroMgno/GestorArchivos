@echo off
cd /d C:\Apps\SDU
echo Instalando dependencias...
pip install -r requirements.txt
echo Iniciando aplicacion Streamlit...
python -m streamlit run main_app.py --server.port=8501 
pause