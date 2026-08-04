from __future__ import annotations

import os
import sqlite3
import smtplib
from datetime import datetime
from email.message import EmailMessage
from pathlib import Path
from typing import Any

from flask import Flask, flash, g, jsonify, redirect, render_template, request, url_for
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR/".env")
DB_PATH = BASE_DIR / "tourism_leads.db"

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-key-change-me")
app.config["OWNER_NAME"] = os.getenv("OWNER_NAME", "Site Owner")
app.config["OWNER_EMAIL"] = os.getenv("OWNER_EMAIL", "owner@example.com")
app.config["SMTP_HOST"] = os.getenv("SMTP_HOST", "")
app.config["SMTP_PORT"] = int(os.getenv("SMTP_PORT", "587"))
app.config["SMTP_USERNAME"] = os.getenv("SMTP_USERNAME", "")
app.config["SMTP_PASSWORD"] = os.getenv("SMTP_PASSWORD", "")
app.config["SMTP_FROM"] = os.getenv("SMTP_FROM", app.config["SMTP_USERNAME"] or "")
app.config["SMTP_USE_TLS"] = os.getenv("SMTP_USE_TLS", "true").lower() == "true"

HERITAGE_SITES = [
    {
        "slug": "royal-fortress",
        "name": "Royal Fortress",
        "category": "Fort",
        "era": "17th Century",
        "timing": "9:00 AM - 6:00 PM",
        "image": "https://images.unsplash.com/photo-1524492412937-b28074a5d7da?auto=format&fit=crop&w=1200&q=80",
        "description": "A hilltop fortress known for panoramic views, military architecture, and royal chambers.",
        "highlights": ["Stone gateways", "Watch towers", "Sunset viewpoint"],
    },
    {
        "slug": "sun-temple",
        "name": "Sun Temple",
        "category": "Temple",
        "era": "12th Century",
        "timing": "6:00 AM - 7:00 PM",
        "image": "https://images.unsplash.com/photo-1548013146-72479768bada?auto=format&fit=crop&w=1200&q=80",
        "description": "A sculpted temple complex famous for its sunrise axis and intricate carvings.",
        "highlights": ["Granite pillars", "Sacred tank", "Carved mandapam"],
    },
    {
        "slug": "old-bazaar",
        "name": "Old Bazaar Street",
        "category": "Market",
        "era": "Colonial",
        "timing": "10:00 AM - 9:00 PM",
        "image": "https://images.unsplash.com/photo-1513635269975-59663e0ac1ad?auto=format&fit=crop&w=1200&q=80",
        "description": "A vibrant market district with spices, textiles, handicrafts, and street food.",
        "highlights": ["Local crafts", "Night lights", "Food lanes"],
    },
    {
        "slug": "river-palace",
        "name": "River Palace",
        "category": "Palace",
        "era": "18th Century",
        "timing": "9:30 AM - 5:30 PM",
        "image": "https://images.unsplash.com/photo-1467269204594-9661b134dd2b?auto=format&fit=crop&w=1200&q=80",
        "description": "A riverside residence blending Indo-European design and ceremonial halls.",
        "highlights": ["Mirror hall", "Royal court", "Waterfront garden"],
    },
    {
        "slug": "heritage-museum",
        "name": "Heritage Museum",
        "category": "Museum",
        "era": "Modern Curation",
        "timing": "10:00 AM - 6:00 PM",
        "image": "https://images.unsplash.com/photo-1518998053901-5348d3961a04?auto=format&fit=crop&w=1200&q=80",
        "description": "An immersive museum featuring artifacts, maps, textiles, and digital exhibits.",
        "highlights": ["Interactive gallery", "Audio stories", "Rare manuscripts"],
    },
    {
        "slug": "lotus-garden",
        "name": "Lotus Heritage Garden",
        "category": "Garden",
        "era": "Restored Estate",
        "timing": "7:00 AM - 7:00 PM",
        "image": "https://images.unsplash.com/photo-1506744038136-46273834b3fb?auto=format&fit=crop&w=1200&q=80",
        "description": "A landscaped heritage garden with lotus ponds, shaded walkways, and musical fountains.",
        "highlights": ["Family-friendly", "Photography spots", "Evening fountain"],
    },
    {
        "slug": "desert-citadel",
        "name": "Desert Citadel",
        "category": "Fort",
        "era": "16th Century",
        "timing": "8:30 AM - 6:30 PM",
        "image": "https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?auto=format&fit=crop&w=1200&q=80",
        "description": "Golden sandstone walls, courtyards, and sweeping desert panoramas.",
        "highlights": ["Ramparts", "Royal gateway", "Evening views"],
    },
    {
        "slug": "emerald-lake-retreat",
        "name": "Emerald Lake Retreat",
        "category": "Nature",
        "era": "Scenic Preserve",
        "timing": "6:00 AM - 6:00 PM",
        "image": "https://images.unsplash.com/photo-1501785888041-af3ef285b470?auto=format&fit=crop&w=1200&q=80",
        "description": "A serene lakeside escape with pine ridges, boating, and sunrise decks.",
        "highlights": ["Lake views", "Boating", "Nature walks"],
    },

    {
        "slug": "eiffel-tower",
        "name": "Eiffel Tower",
        "category": "Monument",
        "era": "1889",
        "timing": "9:30 AM - 11:45 PM",
        "image": "https://images.unsplash.com/photo-1511739001486-6bfe10ce785f?auto=format&fit=crop&w=1200&q=80",
        "description": "The iconic landmark of Paris offering breathtaking panoramic city views.",
        "highlights": ["Paris Skyline", "Night Lights", "Observation Deck"],
    },
    {
        "slug": "colosseum",
        "name": "Colosseum",
        "category": "Historical Monument",
        "era": "80 AD",
        "timing": "8:30 AM - 7:00 PM",
        "image": "https://images.unsplash.com/photo-1552832230-c0197dd311b5?auto=format&fit=crop&w=1200&q=80",
        "description": "Rome's legendary amphitheater and one of the greatest engineering marvels.",
        "highlights": ["Roman History", "Ancient Architecture", "UNESCO Site"],
    },
    {
        "slug": "great-wall",
        "name": "Great Wall of China",
        "category": "Heritage",
        "era": "7th Century BC",
        "timing": "7:30 AM - 5:30 PM",
        "image": "https://images.unsplash.com/photo-1508804185872-d7badad00f7d?auto=format&fit=crop&w=1200&q=80",
        "description": "A magnificent wall stretching thousands of kilometers across China.",
        "highlights": ["Mountain Views", "UNESCO Site", "Historic Wonder"],
    },
    {
        "slug": "taj-mahal",
        "name": "Taj Mahal",
        "category": "Monument",
        "era": "1632",
        "timing": "6:00 AM - 6:30 PM",
        "image": "https://images.unsplash.com/photo-1564507592333-c60657eea523?auto=format&fit=crop&w=1200&q=80",
        "description": "India's iconic marble monument and one of the Seven Wonders of the World.",
        "highlights": ["White Marble", "Sunrise View", "UNESCO Site"],
    },
    {
        "slug": "maldives",
        "name": "Maldives",
        "category": "Beach",
        "era": "Tropical Paradise",
        "timing": "Open All Day",
        "image": "https://images.unsplash.com/photo-1573843981267-be1999ff37cd?auto=format&fit=crop&w=1200&q=80",
        "description": "Luxury overwater villas, turquoise lagoons, and crystal-clear beaches.",
        "highlights": ["Luxury Resorts", "Private Beaches", "Snorkeling"],
    },
    {
        "slug": "santorini",
        "name": "Santorini",
        "category": "Island",
        "era": "Ancient Civilization",
        "timing": "Open All Day",
        "image": "https://images.unsplash.com/photo-1500375592092-40eb2168fd21?auto=format&fit=crop&w=1200&q=80",
        "description": "A romantic Greek island famous for blue domes and spectacular sunsets.",
        "highlights": ["Blue Domes", "Luxury Hotels", "Sunset Cruise"],
    },
    {
        "slug": "bali",
        "name": "Bali",
        "category": "Island",
        "era": "Ancient Culture",
        "timing": "Open All Day",
        "image": "https://images.unsplash.com/photo-1537953773345-d172ccf13cf1?auto=format&fit=crop&w=1200&q=80",
        "description": "Indonesia's tropical paradise filled with temples, beaches, and waterfalls.",
        "highlights": ["Rice Terraces", "Temples", "Surfing"],
    },
    {
        "slug": "swiss-alps",
        "name": "Swiss Alps",
        "category": "Mountain",
        "era": "Natural Wonder",
        "timing": "Open All Day",
        "image": "https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?auto=format&fit=crop&w=1200&q=80",
        "description": "Snow-capped mountains, alpine villages, and world-famous ski resorts.",
        "highlights": ["Cable Cars", "Snow Peaks", "Skiing"],
    },
    {
        "slug": "burj-khalifa",
        "name": "Burj Khalifa",
        "category": "Skyscraper",
        "era": "2010",
        "timing": "8:30 AM - 11:00 PM",
        "image": "https://images.unsplash.com/photo-1512453979798-5ea266f8880c?auto=format&fit=crop&w=1200&q=80",
        "description": "The tallest building in the world with breathtaking views of Dubai.",
        "highlights": ["Sky Deck", "Luxury Shopping", "Dubai Fountain"],
    },
    {
        "slug": "machu-picchu",
        "name": "Machu Picchu",
        "category": "Ancient City",
        "era": "15th Century",
        "timing": "6:00 AM - 5:30 PM",
        "image": "https://images.unsplash.com/photo-1526392060635-9d6019884377?auto=format&fit=crop&w=1200&q=80",
        "description": "Peru's breathtaking Incan citadel hidden among the Andes Mountains.",
        "highlights": ["Mountain Trek", "Ancient Ruins", "UNESCO Site"],
    },
    {
    "slug": "seychelles",
    "name": "Seychelles",
    "category": "Honeymoon",
    "era": "Tropical Paradise",
    "timing": "Open All Day",
    "image": "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=1200&q=80",
    "description": "A romantic island paradise with crystal-clear waters, white sandy beaches, and luxury resorts.",
    "highlights": ["Private Beaches", "Luxury Villas", "Snorkeling"],
},
{
    "slug": "bora-bora",
    "name": "Bora Bora",
    "category": "Honeymoon",
    "era": "Island Paradise",
    "timing": "Open All Day",
    "image": "https://images.unsplash.com/photo-1500375592092-40eb2168fd21?auto=format&fit=crop&w=1200&q=80",
    "description": "A dream honeymoon destination in French Polynesia famous for overwater bungalows.",
    "highlights": ["Overwater Villas", "Lagoon", "Romantic Sunset"],
},
{
    "slug": "mauritius",
    "name": "Mauritius",
    "category": "Honeymoon",
    "era": "Island Escape",
    "timing": "Open All Day",
    "image": "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=1200&q=80",
    "description": "A tropical island offering turquoise lagoons, luxury resorts, and coral reefs.",
    "highlights": ["Beach Resort", "Scuba Diving", "Sunset Cruise"],
},
{
    "slug": "phuket",
    "name": "Phuket",
    "category": "Honeymoon",
    "era": "Modern Paradise",
    "timing": "Open All Day",
    "image": "https://images.unsplash.com/photo-1468413253725-0d5181091126?auto=format&fit=crop&w=1200&q=80",
    "description": "Thailand's most romantic island with beaches, nightlife, and luxury stays.",
    "highlights": ["Island Tours", "Luxury Hotels", "Beach Walk"],
},
{
    "slug": "phi-phi-islands",
    "name": "Phi Phi Islands",
    "category": "Honeymoon",
    "era": "Natural Paradise",
    "timing": "Open All Day",
    "image": "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=1200&q=80",
    "description": "Famous for crystal-clear waters, limestone cliffs, and romantic boat rides.",
    "highlights": ["Boat Ride", "Blue Water", "Photography"],
},
{
    "slug": "capri",
    "name": "Capri",
    "category": "Honeymoon",
    "era": "Italian Island",
    "timing": "Open All Day",
    "image": "https://images.unsplash.com/photo-1500375592092-40eb2168fd21?auto=format&fit=crop&w=1200&q=80",
    "description": "A luxurious Italian island perfect for romantic getaways and yacht cruises.",
    "highlights": ["Blue Grotto", "Luxury Shopping", "Sea View"],
},
{
    "slug": "amalfi-coast",
    "name": "Amalfi Coast",
    "category": "Honeymoon",
    "era": "Italian Heritage",
    "timing": "Open All Day",
    "image": "https://images.unsplash.com/photo-1506744038136-46273834b3fb?auto=format&fit=crop&w=1200&q=80",
    "description": "Colorful cliffside villages overlooking the Mediterranean Sea.",
    "highlights": ["Sea View", "Luxury Hotels", "Romantic Drive"],
},
{
    "slug": "venice",
    "name": "Venice",
    "category": "Honeymoon",
    "era": "Historic City",
    "timing": "Open All Day",
    "image": "https://images.unsplash.com/photo-1516483638261-f4dbaf036963?auto=format&fit=crop&w=1200&q=80",
    "description": "A magical city famous for canals, gondola rides, and romantic architecture.",
    "highlights": ["Gondola Ride", "Canals", "Historic Buildings"],
},
{
    "slug": "paris",
    "name": "Paris",
    "category": "Honeymoon",
    "era": "Romantic Capital",
    "timing": "Open All Day",
    "image": "https://images.unsplash.com/photo-1499856871958-5b9627545d1a?auto=format&fit=crop&w=1200&q=80",
    "description": "The City of Love featuring iconic landmarks, luxury dining, and romantic evenings.",
    "highlights": ["Eiffel Tower", "River Cruise", "Fine Dining"],
},
{
    "slug": "iceland-blue-lagoon",
    "name": "Blue Lagoon",
    "category": "Honeymoon",
    "era": "Natural Spa",
    "timing": "9:00 AM - 9:00 PM",
    "image": "https://images.unsplash.com/photo-1470770841072-f978cf4d019e?auto=format&fit=crop&w=1200&q=80",
    "description": "A world-famous geothermal spa surrounded by volcanic landscapes.",
    "highlights": ["Hot Springs", "Luxury Spa", "Northern Lights"],
},
    {
        "slug": "niagara-falls",
        "name": "Niagara Falls",
        "category": "Waterfall",
        "era": "Natural Wonder",
        "timing": "Open All Day",
        "image": "https://images.unsplash.com/photo-1506744038136-46273834b3fb?auto=format&fit=crop&w=1200&q=80",
        "description": "A world-famous waterfall shared by Canada and the United States.",
        "highlights": ["Boat Ride", "Night Illumination", "Scenic Views"],
    },
    {
        "slug": "mount-fuji",
        "name": "Mount Fuji",
        "category": "Mountain",
        "era": "Natural Wonder",
        "timing": "Open All Day",
        "image": "https://images.unsplash.com/photo-1493976040374-85c8e12f0c0e?auto=format&fit=crop&w=1200&q=80",
        "description": "Japan's iconic volcanic mountain surrounded by lakes and cherry blossoms.",
        "highlights": ["Cherry Blossoms", "Photography", "Hiking"],
    },
    {
        "slug": "pyramids-giza",
        "name": "Pyramids of Giza",
        "category": "Ancient Wonder",
        "era": "2560 BC",
        "timing": "8:00 AM - 5:00 PM",
        "image": "https://images.unsplash.com/photo-1572252009286-268acec5ca0a?auto=format&fit=crop&w=1200&q=80",
        "description": "The last surviving Wonder of the Ancient World located in Egypt.",
        "highlights": ["Camel Ride", "Great Pyramid", "Ancient History"],
    },{
    "slug": "tower-bridge",
    "name": "Tower Bridge",
    "category": "Bridge",
    "era": "1894",
    "timing": "9:30 AM - 6:00 PM",
    "image": "https://images.unsplash.com/photo-1513635269975-59663e0ac1ad?auto=format&fit=crop&w=1200&q=80",
    "description": "One of London's most iconic landmarks, offering stunning views of the River Thames and the city's skyline.",
    "highlights": ["Glass Walkway", "River Thames", "City Views"],
},
{
    "slug": "big-ben",
    "name": "Big Ben & Palace of Westminster",
    "category": "Historical Landmark",
    "era": "1859",
    "timing": "Open All Day (Exterior)",
    "image": "https://images.unsplash.com/photo-1529655683826-aba9b3e77383?auto=format&fit=crop&w=1200&q=80",
    "description": "The world-famous clock tower and the historic seat of the UK Parliament, located beside the River Thames.",
    "highlights": ["Clock Tower", "Parliament", "Photography"],
},{
    "slug": "london-eye",
    "name": "London Eye",
    "category": "Observation Wheel",
    "era": "2000",
    "timing": "11:00 AM - 6:00 PM",
    "image": "https://images.unsplash.com/photo-1517394834181-95ed159986c7?auto=format&fit=crop&w=1200&q=80",
    "description": "A giant observation wheel offering spectacular 360-degree views of London's skyline.",
    "highlights": ["Skyline Views", "River Thames", "Sunset Ride"],
},
{
    "slug": "plitvice-lakes",
    "name": "Plitvice Lakes National Park",
    "category": "Nature",
    "era": "National Park",
    "timing": "7:00 AM - 8:00 PM",
    "image": "https://images.unsplash.com/photo-1501785888041-af3ef285b470?auto=format&fit=crop&w=1200&q=80",
    "description": "Croatia's breathtaking national park featuring turquoise lakes, cascading waterfalls, and lush forests.",
    "highlights": ["Waterfalls", "Wooden Trails", "Crystal Lakes"],
},
{
    "slug": "lake-louise",
    "name": "Lake Louise",
    "category": "Nature",
    "era": "Natural Wonder",
    "timing": "Open All Day",
    "image": "https://images.unsplash.com/photo-1500534314209-a25ddb2bd429?auto=format&fit=crop&w=1200&q=80",
    "description": "A stunning glacier-fed lake in the Canadian Rockies surrounded by snow-capped mountains.",
    "highlights": ["Turquoise Lake", "Mountain Views", "Canoeing"],
},

]


def get_db() -> sqlite3.Connection:
    if "db" not in g:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        g.db = conn
    return g.db


@app.teardown_appcontext
def close_db(_: Any) -> None:
    db = g.pop("db", None)
    if db is not None:
        db.close()



def init_db() -> None:
    db = sqlite3.connect(DB_PATH)
    cursor = db.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT NOT NULL,
            interest_type TEXT NOT NULL,
            travel_date TEXT,
            travelers INTEGER,
            budget TEXT,
            message TEXT,
            source TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'new',
            created_at TEXT NOT NULL
        )
        """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS owner_notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            body TEXT NOT NULL,
            channel TEXT NOT NULL,
            created_at TEXT NOT NULL,
            lead_id INTEGER,
            FOREIGN KEY (lead_id) REFERENCES leads (id)
        )
        """
    )
    db.commit()
    db.close()



def send_owner_email(subject: str, body: str) -> bool:
    if not all([
        app.config["SMTP_HOST"],
        app.config["SMTP_USERNAME"],
        app.config["SMTP_PASSWORD"],
        app.config["SMTP_FROM"],
        app.config["OWNER_EMAIL"],
    ]):
        return False

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = app.config["SMTP_FROM"]
    msg["To"] = app.config["OWNER_EMAIL"]
    msg.set_content(body)

    with smtplib.SMTP(app.config["SMTP_HOST"], app.config["SMTP_PORT"], timeout=20) as server:
        if app.config["SMTP_USE_TLS"]:
            server.starttls()
        server.login(app.config["SMTP_USERNAME"], app.config["SMTP_PASSWORD"])
        server.send_message(msg)
    return True





def send_customer_email(to_email: str, subject: str, body: str) -> bool:
    if not all([
        app.config["SMTP_HOST"],
        app.config["SMTP_USERNAME"],
        app.config["SMTP_PASSWORD"],
        app.config["SMTP_FROM"],
    ]):
        return False

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = app.config["SMTP_FROM"]
    msg["To"] = to_email
    msg.set_content(body)

    with smtplib.SMTP(app.config["SMTP_HOST"], app.config["SMTP_PORT"], timeout=20) as server:
        if app.config["SMTP_USE_TLS"]:
            server.starttls()
        server.login(app.config["SMTP_USERNAME"], app.config["SMTP_PASSWORD"])
        server.send_message(msg)
    return True

def notify_owner(lead_id: int, subject: str, body: str) -> None:
    channel = "saved"
    try:
        if send_owner_email(subject, body):
            channel = "email + saved"
    except Exception as e:
        print(f"Mail Error: {e}")

    db = get_db()
    db.execute(
        "INSERT INTO owner_notifications (title, body, channel, created_at, lead_id) VALUES (?, ?, ?, ?, ?)",
        (subject, body, channel, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), lead_id),
    )
    db.commit()



def save_lead(form: dict[str, Any], source: str) -> int:
    db = get_db()
    cursor = db.execute(
        """
        INSERT INTO leads (
            full_name, email, phone, interest_type, travel_date, travelers, budget, message, source, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            form.get("full_name", "").strip(),
            form.get("email", "").strip(),
            form.get("phone", "").strip(),
            form.get("interest_type", "").strip(),
            form.get("travel_date", "").strip(),
            int(form.get("travelers", 1) or 1),
            form.get("budget", "").strip(),
            form.get("message", "").strip(),
            source,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        ),
    )
    db.commit()
    return int(cursor.lastrowid)



def site_by_slug(slug: str) -> dict[str, Any] | None:
    return next((site for site in HERITAGE_SITES if site["slug"] == slug), None)


@app.route("/")
def home() -> str:
    return render_template("index.html", sites=HERITAGE_SITES[:4])


@app.route("/heritage")
def heritage() -> str:
    return render_template("heritage.html", sites=HERITAGE_SITES)


@app.route("/heritage/<slug>")
def heritage_detail(slug: str) -> str:
    site = site_by_slug(slug)
    if not site:
        return render_template("404.html"), 404
    return render_template("heritage_detail.html", site=site)


@app.route("/gallery")
def gallery() -> str:
    return render_template("gallery.html", sites=HERITAGE_SITES)


@app.route("/booking", methods=["GET", "POST"])
def booking() -> str:
    if request.method == "POST":
        lead_id = save_lead(request.form, "booking")
        subject = f"New booking lead from {request.form.get('full_name', 'Visitor')}"
        body = (
            f"A new booking lead was submitted.\n\n"
            f"Name: {request.form.get('full_name')}\n"
            f"Email: {request.form.get('email')}\n"
            f"Phone: {request.form.get('phone')}\n"
            f"Travel Date: {request.form.get('travel_date')}\n"
            f"Travelers: {request.form.get('travelers')}\n"
            f"Budget: {request.form.get('budget')}\n"
            f"Message: {request.form.get('message')}\n"
        )
        notify_owner(lead_id, subject, body)
        try:
            send_customer_email(
                request.form.get("email"),
                "Booking Request Received",
                f"""Dear {request.form.get('full_name')},

Thank you for choosing us!

We have successfully received your booking request.
Our team will contact you as soon as possible to confirm your booking and discuss the selected package.

Best Regards,
Tourism Portal Team"""
            )
        except Exception as e:
            print(f"Customer Mail Error: {e}")
        flash("Booking enquiry sent successfully. The owner has been notified.", "success")
        return redirect(url_for("booking"))
    return render_template("booking.html")


@app.route("/contact", methods=["GET", "POST"])
def contact() -> str:
    if request.method == "POST":
        lead_id = save_lead(request.form, "contact")
        subject = f"New contact lead from {request.form.get('full_name', 'Visitor')}"
        body = (
            f"Hi Team,\n\n"
            f"A new customer enquiry has been recorded and is currently awaiting review.\n\n"
            f"Name: {request.form.get('full_name')}\n"
            f"Email: {request.form.get('email')}\n"
            f"Phone: {request.form.get('phone')}\n"
            f"Interest: {request.form.get('interest_type')}\n"
            f"Message: {request.form.get('message')}\n"
        )
        notify_owner(lead_id, subject, body)
        try:
            send_customer_email(
                request.form.get("email"),
                "Thank You for Contacting Us",
                f"""Dear {request.form.get('full_name')},

Thank you for choosing us!

We have successfully received your enquiry.
Our team will contact you as soon as possible to discuss the available tour packages.

Best Regards,
Tourism Portal Team"""
            )
        except Exception as e:
            print(f"Customer Mail Error: {e}")
        flash("Thank you. Your contact details have been successfully","recorded. Our team will contact you as soon as possible.")
        return redirect(url_for("contact"))
    return render_template("contact.html")


@app.route("/api/leads/summary")
def leads_summary() -> Any:
    db = get_db()
    result = db.execute(
        "SELECT source, COUNT(*) AS total FROM leads GROUP BY source ORDER BY total DESC"
    ).fetchall()
    return jsonify([{"source": row["source"], "total": row["total"]} for row in result])


@app.errorhandler(404)
def not_found(_: Any) -> tuple[str, int]:
    return render_template("404.html"), 404


if __name__ == "__main__":
    init_db()
    app.run(debug=True)