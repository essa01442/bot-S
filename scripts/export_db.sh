#!/usr/bin/env bash
set -e

echo "Exporting trades to CSV..."
python - << 'EOF'
from core.database import Database
db = Database()
path = db.export_csv('data/trades_export.csv')
print(f"Exported to {path}")
db.close()
EOF
