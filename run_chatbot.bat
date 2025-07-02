@echo off
REM Start Ollama Mistral in the background
start "Ollama Mistral" /MIN cmd /c "ollama run mistral & exit"

REM Wait a few seconds to ensure Ollama is running
ping 127.0.0.1 -n 5 > nul

REM Start the Flask app, auto-close window when done
start "Better Analytics Chatbot" cmd /c "python app.py & exit"

echo Both Ollama Mistral and the chatbot web server are starting...
pause
