from flask import Flask, request, jsonify
import firebase_admin
from firebase_admin import credentials, db
import json
import os
from datetime import datetime

app = Flask(__name__)

firebase_config = json.loads(os.environ["FIREBASE_KEY"])
cred = credentials.Certificate(firebase_config)

firebase_admin.initialize_app(cred, {
    "databaseURL": "https://smartattendance-d74c6-default-rtdb.asia-southeast1.firebasedatabase.app"
})

@app.route("/mark_attendance", methods=["POST"])
def mark_attendance():
    data = request.json
    
    roll_no = data.get("roll_no")
    name = data.get("name")
    department = data.get("department")
    status = data.get("status")

    if not roll_no or not status:
        return jsonify({"error": "Missing required fields"}), 400

    ref = db.reference("attendance")
    ref.push({
        "roll_no": roll_no,
        "name": name,
        "department": department,
        "status": status,
        "timestamp": datetime.now().isoformat()
    })

    return jsonify({"message": "Attendance stored successfully"})
