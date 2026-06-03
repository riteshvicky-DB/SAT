$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)

Start-Process powershell -ArgumentList @(
  "-NoExit",
  "-Command",
  "cd `"$Root\backend`"; if (!(Test-Path .venv)) { python -m venv .venv }; .\.venv\Scripts\Activate.ps1; pip install -r requirements.txt; python scripts\seed.py; uvicorn app.main:app --host 0.0.0.0 --port 8000"
)

cd "$Root\frontend"
npm install
npm run dev
