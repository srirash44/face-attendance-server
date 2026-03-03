from flask import Flask, request, jsonify
import face_recognition
import numpy as np
import firebase_admin
from firebase_admin import credentials, db
import base64
import cv2
import json
import os

app = Flask(__name__)

# 🔐 Load Firebase key from Render Environment Variable
firebase_config = json.loads(os.environ["FIREBASE_KEY"])

cred = credentials.Certificate(firebase_config)
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://smartattendance-d74c6-default-rtdb.asia-southeast1.firebasedatabase.app/'
})

# 🔍 Convert base64 image to face encoding
def get_face_encoding(image_data):
    try:
        img_array = np.frombuffer(base64.b64decode(image_data), np.uint8)
        img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

        if img is None:
            return None

        rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encodings = face_recognition.face_encodings(rgb_img)

        if len(encodings) > 0:
            return encodings[0]

        return None
    except:
        return None


# 🎓 REGISTER FACE
@app.route('/register', methods=['POST'])
def register():
    data = request.json
    regNo = data.get('regNo')
    image_data = data.get('image')

    if not regNo or not image_data:
        return jsonify({"status": "Invalid Data"})

    encoding = get_face_encoding(image_data)

    if encoding is None:
        return jsonify({"status": "No face detected"})

    db.reference("students/" + regNo).update({
        "faceEncoding": encoding.tolist(),
        "faceRegistered": True
    })

    return jsonify({"status": "Face Registered"})


# 🧠 VERIFY FACE
@app.route('/verify', methods=['POST'])
def verify():
    data = request.json
    image_data = data.get('image')

    if not image_data:
        return jsonify({"status": "Invalid Data"})

    unknown_encoding = get_face_encoding(image_data)

    if unknown_encoding is None:
        return jsonify({"status": "No face detected"})

    students = db.reference("students").get()

    if students is None:
        return jsonify({"status": "No Students Found"})

    for regNo, details in students.items():
        if "faceEncoding" in details:
            known_encoding = np.array(details["faceEncoding"])
            distance = np.linalg.norm(known_encoding - unknown_encoding)

            if distance < 0.6:
                return jsonify({
                    "status": "Match",
                    "regNo": regNo
                })

    return jsonify({"status": "No Match"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
