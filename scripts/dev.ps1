$root = Split-Path -Parent $PSScriptRoot

Start-Process -FilePath "powershell" -ArgumentList "-NoExit", "-Command", "cd `"$root\backend`"; python -m pip install -r requirements.txt; uvicorn main:app --reload --host 0.0.0.0 --port 8000"
Start-Process -FilePath "powershell" -ArgumentList "-NoExit", "-Command", "cd `"$root\frontend`"; npm install; npm run dev"
