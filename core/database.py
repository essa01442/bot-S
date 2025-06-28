import os
from sqlalchemy import (
    create_engine, Column, Integer, String, Float, DateTime
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import yaml

# تحميل إعدادات الاتصال
cfg = yaml.safe_load(open('config/config.yaml', 'r'))
DB_URL = cfg['database']['url']

# إنشاء المحرك والـ Session
engine = create_engine(DB_URL, pool_size=20, max_overflow=0)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Trade(Base):
    __tablename__ = 'trades'
    id            = Column(Integer, primary_key=True, index=True)
    timestamp     = Column(DateTime, default=datetime.utcnow)
    symbol        = Column(String, index=True)
    action        = Column(String)
    quantity      = Column(Float)
    order_type    = Column(String)
    status        = Column(String)
    avg_fill_price= Column(Float)

def init_db():
    """إنشاء الجداول إذا لم تكن موجودة."""
    Base.metadata.create_all(bind=engine)

class Database:
    def __init__(self):
        init_db()
        self.session = SessionLocal()

    def log_trade(self, trade):
        """سجّل صفقة جديدة."""
        t = Trade(
            symbol=trade.contract.symbol,
            action=trade.order.action,
            quantity=trade.order.totalQuantity,
            order_type=trade.order.orderType,
            status=trade.orderStatus.status,
            avg_fill_price=getattr(trade.orderStatus, 'avgFillPrice', None)
        )
        self.session.add(t)
        self.session.commit()

    def export_csv(self, path='data/trades_export.csv'):
        """صدّر جميع الصفقات إلى CSV."""
        import pandas as pd
        df = pd.read_sql_table('trades', DB_URL)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        df.to_csv(path, index=False)
        return path

    def close(self):
        self.session.close()
