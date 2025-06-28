from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
import os
import yaml
from core.database import Database

# تحميل الإعدادات
cfg = yaml.safe_load(open('config/config.yaml', 'r'))
EXPORT_PATH = 'data/trades_export.csv'

app = FastAPI(title="bot-S Trade API")

@app.on_event("startup")
def startup_event():
    # عند بدء الخدمة نصدّر CSV تلقائيًا
    db = Database()
    db.export_csv(EXPORT_PATH)
    db.close()

@app.get("/trades/download", summary="Download trades CSV")
def download_trades():
    if not os.path.exists(EXPORT_PATH):
        raise HTTPException(status_code=404, detail="Export file not found")
    return FileResponse(EXPORT_PATH, media_type='text/csv', filename='trades_export.csv')

@app.get("/health", summary="Health check")
def health():
    return {"status": "ok"}
feat: add FastAPI endpoint for CSV download
