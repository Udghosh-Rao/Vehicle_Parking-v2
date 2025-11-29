In my project, I run 4 terminals.
# Terminal 1 — Flask Backend API
 cd backend python app.py



# Terminal 2 — VueJS Frontend

cd frontend 
npm run dev


# Terminal 3 — Redis Server
manually open 


# Terminal 4 — Celery Worker

cd backend 

celery -A celery_app.celery worker -l info -P solo


Executes async tasks

Runs daily reminder email

Runs monthly report

Generates CSV export asynchronously

# Terminal 5 — Celery Beat


celery -A celery_app.celery beat -l info


Schedules daily reminder

Schedules monthly report

Schedules cache refresh

# Terminal 6 — MailHog (or SMTP debug server)
MailHog.exe

http://localhost:8025
python mail.py


Shows all emails (daily reminder, booking confirmation, monthly report)
