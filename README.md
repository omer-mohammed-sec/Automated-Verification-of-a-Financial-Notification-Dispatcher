# Financial Notification Dispatcher API

**مشروع التحقق الآلي واختبار النظام (Software Verification & Testing API)**  
**رقم القيد (Registration Number):** `30027/2025`  

---

## 📌 وصف المشروع (Project Description)

هذا المشروع يوفر نظام إرسال وإدارة التنبيهات المالية (`Notification Engine API`) والتحقق الآلي منها. يتضمن النظام آليات إعادة المحاولة عبر بوابات الاتصال الأساسية والاحتياطية، فحص التكرار (Idempotency)، واختبارات تكامل شاملة مع قاعدة بيانات SQLite واختبارات أداء واختبارات وحدة معزولة (Unit & Integration Tests).

---

## 📋 المتطلبات (Requirements)

المتطلبات المحددة في ملف `requirements.txt`:

```text
pytest
pytest-cov
```

---

## 🛠️ خطوات التثبيت والتشغيل (Installation & Running Instructions)

### 1. إنشاء وتفعيل البيئة الافتراضية (Virtual Environment)
```bash
python -m venv venv

# على نظام Windows PowerShell:
.\venv\Scripts\Activate.ps1

# على نظام Linux / macOS:
source venv/bin/activate
```

### 2. تثبيت الحزم والمتطلبات (Install Requirements)
```bash
pip install -r requirements.txt
```

### 3. تشغيل الاختبارات (Run Tests)
```bash
pytest -v
```

### 4. تشغيل تقارير التغطية (Run Coverage Report)
```bash
pytest --cov=. --cov-report=term-missing --cov-fail-under=90
```

---

## 📂 هيكلة المشروع (Project Structure)

```text
financial_notification_dispatcher/
├── notification_engine.py      # كود تطبيق المحرك الأساسي (Core Application Logic)
├── requirements.txt            # ملف الحزم والمتطلبات (Project Dependencies)
├── pytest.ini                  # إعدادات مشغل الاختبارات (Pytest Configuration)
├── conftest.py                 # إعداد مسارات استيراد الوحدات (Python Path Setup)
├── .gitignore                  # استثناءات git لبيئة بايثون (Git Exclusions)
├── README.md                   # التوثيق الشامل للمشروع ورقم القيد
├── docs/                       # مجلد التوثيق والتقارير (Documentation & Reports)
│   └── report.html             # تقرير الاختبارات (Test Report HTML)
├── tests/                      # مجلد اختبارات النظام (Test Suite Directory)
│   ├── test_unit.py            # اختبارات الوحدة المعزولة (Unit Tests)
│   └── test_integration.py     # اختبارات التكامل مع SQLite (Integration Tests)
└── .github/
    └── workflows/
        └── ci.yml              # خط أنابيب التجميع والتكامل المستمر (CI Workflow)
```
