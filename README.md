الآن وقد أصبح الروبوت قابلاً للتشغيل الدائم داخل حاوية Docker مع سياسة إعادة التشغيل **restart: always**، يبقى علينا:

1. **كتابة ملف README.md** يشرح:

   * بنية المشروع
   * كيفية الإعداد المحلي وداخل Docker
   * تشغيل الخدمة والـ Dashboard
   * نقاط النهاية للـ API
   * كيفية الوصول إلى تقارير الصفقات والمخاطر

2. **إعداد CI/CD بسيط** ليتحقق من بناء الصورة ودفعها إلى Registry (Docker Hub أو GitHub Container Registry).

3. **تأمين المتغيرات السرية** (DB credentials, IBKR clientId) في GitHub Secrets أو في ملفات بيئة خارجية.

---

## 1. مسودة `README.md`

أنشئ في جذر المستودع `README.md` بالمحتوى التالي:

```markdown
# bot-S

روبوت تداول آلي للأسهم الأمريكية (سكالبنج، تحليل كمي وذكاء اصطناعي).

## المزايا

- استراتيجية سكالبنج (EMA crossover) مدعومة بـ AI (FinRL + Qlib).  
- تنفيذ حي على Interactive Brokers عبر `ib_insync`.  
- إدارة مخاطر (drawdown, max drawdown) وتوليد تقارير HTML.  
- واجهة API لتحميل الصفقات وتقارير المخاطر.  
- Dashboard تفاعلي بـ Streamlit.  
- يعمل داخل Docker مع `restart: always`.

## الهيكل

```

bot-S/
├── api/              # FastAPI endpoints
├── ai/               # نموذج التنبؤ (FinRL + Qlib)
├── core/
│   ├── database.py   # SQLAlchemy DB wrapper
│   └── risk\_manager.py
├── config/           # config.yaml (DB & server)
├── dashboard/        # Streamlit app
├── engines/
│   ├── backtester.py
│   └── executor.py   # IBKR live execution
├── reports/          # HTML reports
├── scripts/
│   └── setup\_env.sh
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── run\_bot.py        # main loop

````

## المتطلبات

- Docker & Docker Compose  
- حساب Interactive Brokers (TWS/Gateway)  
- قاعدة PostgreSQL أو أي DSN مدعوم  

## الإعداد

1. اضبط `config/config.yaml`:
   ```yaml
   database:
     url: postgresql://<USER>:<PASS>@<HOST>:5432/<DB>
   server:
     host: 0.0.0.0
     port: 8000
````

2. انسخ ملف الـ secrets (إن وجدت) إلى GitHub Secrets أو `.env`.

## التشغيل داخل Docker

```bash
docker-compose up --build -d
```

* API على: `http://<SERVER_IP>:8000`

  * `GET /health`
  * `GET /trades/download`
  * `GET /risk/report`

* Dashboard على: `http://<SERVER_IP>:8501`

## التشغيل محلياً (بدون Docker)

```bash
pip install -r requirements.txt
mkdir -p data reports
python run_bot.py
```

ثم:

```bash
uvicorn api.main:app --host 0.0.0.0 --port 8000 &
streamlit run dashboard/app.py --server.port 8501
```

## CI/CD مقترح

* GitHub Actions لبناء الصورة (`docker build`) ودفعها إلى Registry.
* التفعيل التلقائي على كل `push` إلى `main`.

---

```

---

## 2. الإضافة إلى المستودع

- ارفع `README.md` عبر GitHub UI أو CLI.  
- تأكد من تنسيق Markdown وعرض الروابط والمسارات بشكل صحيح.

---

عند انتهائك، سيكون لديك وثيقة شاملة تسهل على أي شخص (أنت أو فريقك) فهم المشروع وإعداده وتشغيله. أخبرني إذا تريد تعديلاً أو إضافة تفاصيل أخرى!
```
