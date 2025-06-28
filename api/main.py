from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
import os, yaml

from core.database import Database
from core.risk_manager import RiskManager

# Load config
with open('config/config.yaml') as f:
    cfg = yaml.safe_load(f)
DB_URL = cfg['database']['url']
SERVER_HOST = cfg['server']['host']
SERVER_PORT = cfg['server']['port']

app = FastAPI(title="bot-S API")

@app.on_event("startup")
def startup_event():
    # Initialize DB connection (creates tables) and export latest CSV
    db = Database(DB_URL)
    rm = RiskManager()
    db.close()
    rm.export_csv = lambda path='data/trades_export.csv': rm.generate_report(path)

@app.get("/health", summary="Health check")
def health():
    return {"status": "ok"}

@app.get("/trades/download", summary="Download trades CSV")
def download_trades():
    path = 'data/trades_export.csv'
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(path, media_type='text/csv', filename='trades_export.csv')

@app.get("/risk/report", summary="Download risk report")
def download_risk_report():
    path = 'reports/risk_report.html'
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(path, media_type='text/html', filename='risk_report.html')
