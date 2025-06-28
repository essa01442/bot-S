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

