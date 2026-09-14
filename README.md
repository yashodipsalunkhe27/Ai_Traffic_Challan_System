# 🚦 AI Traffic Challan System

An AI-powered traffic violation detection and e-Challan generation system built with Streamlit and vision-language models. Upload a traffic violation image, and the system automatically detects the violation type, reads the vehicle's number plate, looks up the registered owner, calculates the fine, and generates a downloadable PDF challan — all in one flow.

> **Demo project** — built for learning and portfolio purposes. Not affiliated with any government traffic authority or the actual RTO/Parivahan system.

---

## 🎯 What It Does

1. **Upload** a traffic violation image (JPG/PNG).
2. **AI detects** the violation type — *No Helmet*, *Triple Ride*, *No Parking*, or *Overspeed*.
3. **AI reads** the vehicle's number plate, validated against the standard Indian plate format.
4. **System looks up** the registered owner from a local vehicle database.
5. **Challan is generated** with a unique challan number, fine amount, and timestamp.
6. **Owner is notified** via a pre-filled WhatsApp message containing the official e-Challan verification link.
7. **PDF challan** (with QR code linking to the official portal) is available for download.
8. **History and analytics** dashboards track every challan issued, payment status, and revenue trends.

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Frontend / App | Streamlit (multi-page app) |
| AI Vision Model | Groq API — `qwen/qwen3.6-27b` (vision-capable, non-thinking mode) |
| Database | SQLite (`Chalan.db` for violations/challans, `user.db` for vehicle owners) |
| PDF Generation | fpdf2 |
| QR Codes | qrcode |
| Data Handling | pandas |
| Config | python-dotenv / Streamlit Secrets |

---

## ✨ Key Features

- **Violation classification** across 4 categories, with fine amounts pulled from a database table.
- **Indian number-plate validation** — plates are checked against the standard `XX00XX0000` format; anything that doesn't match (foreign plates, unreadable plates, hallucinated output) is explicitly rejected rather than guessed.
- **AI confidence scoring** — a second model pass rates how confident the detection is, so low-confidence results are visibly flagged instead of presented as fact.
- **Challan history** — every generated challan is persisted with a unique challan number, timestamp, and payment status (Paid/Unpaid), browsable on a dedicated history page.
- **Analytics dashboard** — violation-type breakdown, paid vs. pending revenue, and a daily revenue trend chart.
- **PDF challan with QR code** — a downloadable, print-ready challan document linking to the official government e-Challan portal.
- **Live system stats** — KPI cards on the home page reflect real totals from the database, not static placeholders.
- **Reset control** — a confirm-before-delete admin action to clear all challan records for fresh demos.
- **Responsive UI** — usable on both desktop and mobile, with touch-friendly controls.

---

## 🧠 Engineering Notes & Guardrails

A few real-world reliability issues came up while building this, and the fixes are worth calling out:

- **Reasoning-model truncation bug:** the vision model defaults to "thinking mode," which was getting cut off mid-reasoning by a low `max_tokens` limit — causing partial chain-of-thought text to be mistaken for the final answer. Fixed by explicitly setting `reasoning_effort="none"` for classification calls.
- **Prompt-induced hallucination:** an earlier number-plate prompt assumed a specific vehicle position in the frame, causing wrong plate reads on differently composed images. Replaced with a generic, position-agnostic instruction.
- **No-guess policy for unreadable/foreign plates:** the model is explicitly allowed to return `NOTFOUND` instead of being forced to always output *something* — and the app checks this **before** rendering any violation or confidence UI, so an unprocessable image never shows a misleadingly confident (but wrong) result.

---

## ⚠️ Known Limitations

- **Overspeed detection** is inherently limited from a single still image — a production system would use radar-based or ANPR speed-camera data instead of visual inference.
- **SQLite persistence** is local to the running instance. On ephemeral hosting (e.g. Streamlit Community Cloud), challan history may reset between deployments — a production system would use a hosted database such as PostgreSQL.
- **Vision-model accuracy** depends on image clarity, angle, and lighting — like any single-model classification system, it is not guaranteed to be 100% accurate and includes a confidence score for transparency rather than a false guarantee of correctness.

---

## 🚀 Running Locally

```bash
git clone https://github.com/yashodipsalunkhe27/Ai_Traffic_Challan_System.git
cd Ai_Traffic_Challan_System
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
```

Create a `.env` file in the project root:
```
GROQ_API_KEY=your_groq_api_key_here
```

Run the app:
```bash
streamlit run app.py
```

---

## 📁 Project Structure

```
Ai_Traffic_Challan_System/
├── app.py                     # Main Streamlit app
├── violation_detection.py     # AI detection, DB, PDF & challan logic
├── create_database.py         # Seeds user.db with sample vehicle owners
├── Chalan.database.py         # Seeds Chalan.db with violation/fine data
├── pages/
│   ├── Challan_History.py     # Challan history + payment status
│   ├── Analytics.py           # Violation & revenue analytics
│   └── User_Database.py       # Registered vehicle owner directory
├── drivers/                   # Sample driver photos
├── images/                    # Sample test images
├── Chalan.db                  # Violations & challans database
├── user.db                    # Vehicle owner database
└── requirements.txt
```

---

## 📸 Screenshots

<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/0cd186d2-35e9-476a-85ec-cf5640d7ad06" />
<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/d9c62094-8d48-423b-bd5b-b11433caa792" />
<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/49a1d6f8-bb43-49ad-8f19-f746cac16b44" />
<img width="1401" height="850" alt="image" src="https://github.com/user-attachments/assets/4cf76a1b-b23b-414a-8e5e-0409b1898a65" />




---

## 🌐 Live Demo

*(Add your Streamlit Community Cloud link here once deployed)*

---

## 📄 License

This project is for educational and portfolio purposes.

**If you like this project, a ⭐ on the repo would mean a lot. Thanks for checking it out!**
