@echo off
echo Installing requirements...
pip install -r requirements.txt

echo.
echo ==============================================================
echo IMPORTANT: Make sure you have Ollama installed and running!
echo You can get Ollama from: https://ollama.com/
echo.
echo Make sure you have pulled a model, for example 'llama3' or 'qwen2'.
echo Command: ollama run llama3
echo ==============================================================
echo.

echo Starting Real-time Translator...
python translator_app.py
pause
