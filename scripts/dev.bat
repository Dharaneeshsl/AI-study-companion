@echo off
set "ROOT=%~dp0.."

start powershell -NoExit -Command "cd '%ROOT%\backend'; python -m pip install -r requirements.txt; uvicorn main:app --reload --host 0.0.0.0 --port 8000"
start powershell -NoExit -Command "cd '%ROOT%\frontend'; npm install; npm run dev"
