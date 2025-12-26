#  Vehicle Parking System v2

A full-stack **Vehicle Parking Management System** built with **Flask (Python)** for the backend and **Vue.js** for the frontend.  
The system supports **asynchronous background tasks** using **Celery + Redis** and includes **email notifications and reports**.

This project is designed to simulate a real-world parking management platform with slot booking, reports, and automated tasks.

---

##  Features

-  Park & Un-park vehicles  
-  Manage parking slots  
-  Generate parking reports  
-  Background jobs using Celery  
-  Redis for fast task processing  
-  Email notifications (MailHog for development)  
-  REST API + Vue.js frontend  

---

##  Tech Stack

| Layer | Technology |
|------|-----------|
| Backend | Python, Flask |
| Frontend | Vue.js |
| Background Jobs | Celery |
| Message Broker | Redis |
| Email (Dev) | MailHog |

---

##  Project Structure
Vehicle_Parking-v2/
│
├── backend/ # Flask backend & Celery tasks
├── frontend/ # Vue.js frontend
├── README.md
└── ...


---

## ⚙️ Prerequisites

Make sure you have installed:

- Python 3.8+
- Node.js + npm
- Redis
- MailHog (optional, for viewing emails)

---

##  How to Run (Development Mode)

Open **multiple terminals** and follow these steps.

---

### 1️⃣ Start Redis

redis-server

2️⃣ Start Backend (Flask)
cd backend
pip install -r requirements.txt
python app.py


Backend runs at:

http://localhost:5000

3️⃣ Start Frontend (Vue)
cd frontend
npm install
npm run dev


Frontend runs at:

http://localhost:3000

4️⃣ Start Celery Worker

Open a new terminal:

cd backend
celery -A celery_app.celery worker -l info -P solo

5️⃣ Start Celery Beat (Scheduler)
cd backend
celery -A celery_app.celery beat -l info


This runs scheduled jobs like reminders and reports.

6️⃣ Start MailHog (Optional – Email Viewer)

Run MailHog and open:

http://localhost:8025


Then in backend:

python mail.py


All sent emails will appear in MailHog.

🔑 Environment Variables

Create a .env file (or export manually):

FLASK_ENV=development
SECRET_KEY=your_secret_key
REDIS_URL=redis://localhost:6379/0
MAIL_HOST=localhost
MAIL_PORT=1025

📡 API Examples
Endpoint	Method	Purpose
/login	POST	User login
/park	POST	Park a vehicle
/unpark	POST	Unpark a vehicle
/slots	GET	View parking slots
/report	GET	Parking report

(Actual routes are implemented in backend.)

🧠 System Architecture
User → Vue Frontend → Flask API → Database
                         ↓
                     Celery
                         ↓
                       Redis
                         ↓
                   Email / Reports

# Why Celery is Used?

Some operations (email, reports, CSV exports) take time.
Celery runs these in the background without blocking the main API.

# Future Improvements

Add authentication (JWT)

Docker support

Payment integration

Admin dashboard

Production deployment guide

# License

This project is open-source and free to use under the MIT License.

👨‍💻 Author

Udghosh Rao
GitHub: https://github.com/Udghosh-Rao


---

If you want, I can also give you:
- `docker-compose.yml`
- `.env.example`
- API documentation format
- Or a **professional project description for resume / LinkedIn** 😎



