from flask import Flask, render_template, request, jsonify
import requests
import json
import random
from datetime import datetime
from flask import Flask, request
from twilio.rest import Client

app = Flask(__name__)

# ─── Twilio Config ─────────────────────────────────────────────────────────────
import os
TWILIO_ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN  = os.environ.get("TWILIO_AUTH_TOKEN")
TWILIO_FROM_NUMBER = os.environ.get("TWILIO_FROM_NUMBER")
MY_PHONE_NUMBER    = os.environ.get("MY_PHONE_NUMBER")

def send_sms(body: str) -> bool:
    try:
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        client.messages.create(body=body, from_=TWILIO_FROM_NUMBER, to=MY_PHONE_NUMBER)
        return True
    except Exception as e:
        print(f"[Twilio Error] {e}")
        return False


def get_earthquakes():
    try:
        url = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/significant_month.geojson"
        r = requests.get(url, timeout=5)
        data = r.json()
        quakes = []
        for f in data["features"][:10]:
            p = f["properties"]
            c = f["geometry"]["coordinates"]
            quakes.append({
                "place": p.get("place", "Unknown"),
                "mag": p.get("mag", 0),
                "time": datetime.fromtimestamp(p["time"] / 1000).strftime("%d %b %Y, %H:%M"),
                "lat": c[1], "lng": c[0],
                "url": p.get("url", ""),
                "depth": c[2],
                "alert": p.get("alert") or "green"
            })
        return quakes
    except:
        return [
            {"place": "Turkey", "mag": 6.2, "time": "17 May 2025", "lat": 38.9, "lng": 35.2, "depth": 10, "alert": "orange"},
            {"place": "Japan", "mag": 5.8, "time": "16 May 2025", "lat": 35.6, "lng": 139.7, "depth": 30, "alert": "green"},
            {"place": "Indonesia", "mag": 6.8, "time": "15 May 2025", "lat": -6.2, "lng": 106.8, "depth": 20, "alert": "red"},
        ]

SHELTERS = [
    {"name": "Chandigarh Relief Camp", "lat": 30.7333, "lng": 76.7794, "capacity": 500, "available": 320, "type": "flood"},
    {"name": "Delhi Emergency Shelter", "lat": 28.6139, "lng": 77.2090, "capacity": 1000, "available": 650, "type": "earthquake"},
    {"name": "Mumbai Cyclone Centre", "lat": 19.0760, "lng": 72.8777, "capacity": 800, "available": 200, "type": "cyclone"},
    {"name": "Chennai Flood Relief", "lat": 13.0827, "lng": 80.2707, "capacity": 600, "available": 410, "type": "flood"},
    {"name": "Kolkata Storm Centre", "lat": 22.5726, "lng": 88.3639, "capacity": 750, "available": 530, "type": "cyclone"},
    {"name": "Jaipur Desert Camp", "lat": 26.9124, "lng": 75.7873, "capacity": 400, "available": 300, "type": "heatwave"},
    {"name": "Bengaluru Earthquake Hub", "lat": 12.9716, "lng": 77.5946, "capacity": 550, "available": 400, "type": "earthquake"},
    {"name": "Hyderabad Flood Shelter", "lat": 17.3850, "lng": 78.4867, "capacity": 700, "available": 480, "type": "flood"},
]

def ai_response(msg):
    msg = msg.lower()
    if any(w in msg for w in ["earthquake", "quake", "bhukamp"]):
        return "🔴 EARTHQUAKE PROTOCOL:\n• DROP to the ground immediately\n• COVER under sturdy table/desk\n• HOLD ON until shaking stops\n• Stay away from windows & heavy objects\n• After shaking: Check for injuries, gas leaks\n• Move to open area away from buildings\n• Call emergency: 112"
    elif any(w in msg for w in ["flood", "baarish", "pani", "water"]):
        return "🔵 FLOOD EMERGENCY:\n• Move to higher ground IMMEDIATELY\n• Do NOT walk in moving water\n• Avoid driving through flooded roads\n• Turn off utilities at main switches\n• Emergency: 1078 (NDRF Helpline)"
    elif any(w in msg for w in ["cyclone", "hurricane", "storm", "aandhi"]):
        return "🌀 CYCLONE SAFETY:\n• Stay indoors away from windows\n• Cyclone Helpline: 1070"
    elif any(w in msg for w in ["fire", "aag", "burn"]):
        return "🔥 FIRE EMERGENCY:\n• Call Fire Brigade: 101 IMMEDIATELY"
    elif any(w in msg for w in ["shelter", "camp", "sharan"]):
        return "🏕️ FINDING SHELTER:\n• Use our Shelter Finder page (Map tab)\n• Call NDRF: 011-24363260"
    elif any(w in msg for w in ["help", "emergency", "sos", "bachao"]):
        return "🆘 EMERGENCY CONTACTS:\n• Police: 100\n• Ambulance: 108\n• Fire: 101\n• Disaster Helpline: 1078"
    else:
        return "🤖 ResQNet AI Assistant here! Type your disaster type and I'll guide you!"

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/api/earthquakes")
def earthquakes():
    return jsonify(get_earthquakes())

@app.route("/api/shelters")
def shelters():
    return jsonify(SHELTERS)

@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.json
    msg = data.get("message", "")
    reply = ai_response(msg)
    return jsonify({"reply": reply, "time": datetime.now().strftime("%H:%M")})

@app.route("/api/alerts")
def alerts():
    alerts_list = [
        {"id": 1, "type": "earthquake", "severity": "high", "title": "M6.2 Earthquake", "location": "Uttarakhand, India", "time": "2 hrs ago", "desc": "Magnitude 6.2 earthquake detected.", "color": "#FF2D2D"},
        {"id": 2, "type": "flood", "severity": "medium", "title": "Flood Warning", "location": "Bihar, India", "time": "5 hrs ago", "desc": "Heavy rainfall causing river overflow.", "color": "#FF6B00"},
        {"id": 3, "type": "cyclone", "severity": "high", "title": "Cyclone Alert", "location": "Odisha Coast", "time": "1 hr ago", "desc": "Cyclone approaching coast. Wind speed 140 km/h.", "color": "#FF2D2D"},
        {"id": 4, "type": "heatwave", "severity": "low", "title": "Heatwave Advisory", "location": "Rajasthan", "time": "12 hrs ago", "desc": "Temperature above 46°C.", "color": "#FFD600"},
        {"id": 5, "type": "landslide", "severity": "medium", "title": "Landslide Risk", "location": "Himachal Pradesh", "time": "3 hrs ago", "desc": "Heavy rain triggering landslides.", "color": "#FF6B00"},
        {"id": 6, "type": "flood", "severity": "high", "title": "Flash Flood Alert", "location": "Kerala", "time": "30 min ago", "desc": "Flash floods in Wayanad district.", "color": "#FF2D2D"},
    ]
    return jsonify(alerts_list)

@app.route("/help", methods=["GET", "POST"])
def help_page():
    if request.method == "POST":
        return render_template("help.html", success=True)
    return render_template("help.html")

@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name        = request.form.get("name", "").strip()
        phone       = request.form.get("phone", "").strip()
        location    = request.form.get("location", "").strip()
        disaster    = request.form.get("disaster", "Unknown")
        urgency     = request.form.get("urgency", "Normal")
        message     = request.form.get("message", "").strip()
        submitted_at = datetime.now().strftime("%d %b %Y, %H:%M")

        sms_body = (
            f"🆘 ResQNet CONTACT REQUEST\n"
            f"─────────────────────\n"
            f"👤 Name     : {name}\n"
            f"📞 Phone    : {phone}\n"
            f"📍 Location : {location}\n"
            f"⚠️  Disaster : {disaster}\n"
            f"🚨 Urgency  : {urgency}\n"
            f"💬 Message  : {message}\n"
            f"🕐 Time     : {submitted_at}"
        )
        print("\n" + "="*40 + "\n" + sms_body + "\n" + "="*40 + "\n")
        sms_sent = send_sms(sms_body)
        return render_template("contact.html", success=True, sms_sent=sms_sent, name=name)
    return render_template("contact.html", success=False)


def get_address_from_coords(lat, lng):
    try:
        url = f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lng}&format=json"
        headers = {"User-Agent": "ResQNet-App/1.0"}
        r = requests.get(url, headers=headers, timeout=5)
        data = r.json()
        return data.get("display_name", "Address not found")
    except:
        return "Address could not be fetched"


@app.route('/send_alert', methods=['POST'])
def send_alert():
    data = request.get_json()
    latitude  = data.get('latitude')
    longitude = data.get('longitude')
    name      = data.get('name', 'SOS User')
    phone     = data.get('phone', 'N/A')

    if latitude is None or longitude is None:
        return jsonify({"status": "error", "message": "Location not received"}), 400

    address    = get_address_from_coords(latitude, longitude)
    alert_time = datetime.now().strftime("%d %b %Y, %H:%M:%S")

    # ── KEY: /maps/search/?api=1&query= link WhatsApp pe MAP PREVIEW dikhata hai ──
    gmaps_pin = f"https://www.google.com/maps/search/?api=1&query={latitude},{longitude}"
    gmaps_nav = f"https://www.google.com/maps/dir/?api=1&destination={latitude},{longitude}"

    msg_body = (
        f"🆘 *SOS EMERGENCY — ResQNet*\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"👤 *Name*  : {name}\n"
        f"📞 *Phone* : {phone}\n"
        f"🕐 *Time*  : {alert_time}\n\n"
        f"📍 *Exact Address:*\n{address}\n\n"
        f"🗺 *MAP PE DEKHO* (tap karke location dekho):\n"
        f"{gmaps_pin}\n\n"
        f"🧭 *NAVIGATE KARO* (tap karke directions lo):\n"
        f"{gmaps_nav}\n\n"
        f"📌 *Coordinates:* {latitude:.6f}, {longitude:.6f}\n\n"
        f"⚠️ *PLEASE RESPOND IMMEDIATELY!*"
    )

    try:
        twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        twilio_client.messages.create(
            body=msg_body,
            from_=TWILIO_FROM_NUMBER,
            to=MY_PHONE_NUMBER
        )
        print("[SOS SENT]\n" + msg_body)
        return jsonify({"status": "sent", "address": address, "map": gmaps_pin})
    except Exception as e:
        print(f"[Twilio Error in send_alert] {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True, port=5000)
