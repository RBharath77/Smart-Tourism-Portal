# Tourism Portal Pro

A professional tourism website upgraded from the original static project.

## Features
- Professional, unique color theme
- Modern responsive UI
- Heritage listing and detail pages
- Gallery page
- Booking enquiry form
- Contact lead form
- SQLite database to store contact and booking leads
- Owner notification flow when a new lead arrives
- Lead notification storage to view leads and notifications
- Optional SMTP email alert to the owner

## Run locally
```bash
cd upgraded_tourism_portal
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
```

Open:
- Home: `http://127.0.0.1:5000/`
- Admin: `http://127.0.0.1:5000`

## Optional owner email notification
Set these before running if you want the owner to receive email alerts:
```bash
export OWNER_NAME="Bharath"
export OWNER_EMAIL="bharathrajagopal275@gmail.com"
export SMTP_HOST="smtp.gmail.com"
export SMTP_PORT="587"
export SMTP_USERNAME="warbytes7@gmail.com"
export SMTP_PASSWORD="xehb yxys gair xisx"
export SMTP_FROM="warbytes7@gmail.com"
export SMTP_USE_TLS="true"
```

Without SMTP, the lead is still stored in the database and a dashboard notification is created.

## Database
The SQLite database file is created automatically:
- `tourism_leads.db`
