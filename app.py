"""
app.py  –  Medical Blockchain Web Server
Flask REST API + serves the frontend HTML.

Run:  python app.py
Then open:  http://<your-ip>:5000
"""

import json
import threading
from functools import wraps
from datetime import datetime

from flask import Flask, request, jsonify, send_from_directory, send_file
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from blockchain import Blockchain

app = Flask(__name__, static_folder="static")
blockchain = Blockchain()
lock = threading.Lock()
port = int(os.environ.get("PORT", 5000))

# ------------------------------------------------------------------ #
#  CORS  (allow any origin so multiple machines can connect)          #
# ------------------------------------------------------------------ #
@app.after_request
def add_cors(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type,Authorization"
    response.headers["Access-Control-Allow-Methods"] = "GET,POST,OPTIONS"
    return response

@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve_frontend(path):
    static_dir = os.path.join(os.path.dirname(__file__), "static")
    target = os.path.join(static_dir, path)
    if path and os.path.exists(target):
        return send_from_directory(static_dir, path)
    return send_from_directory(static_dir, "index.html")

# ------------------------------------------------------------------ #
#  Helper                                                              #
# ------------------------------------------------------------------ #
def api(f):
    """Wrap handler in JSON response + lock."""
    @wraps(f)
    def wrapper(*args, **kwargs):
        with lock:
            try:
                result = f(*args, **kwargs)
                return jsonify(result)
            except Exception as e:
                return jsonify({"success": False, "error": str(e)}), 500
    return wrapper

def body():
    return request.get_json(force=True, silent=True) or {}

# ------------------------------------------------------------------ #
#  Patient endpoints                                                   #
# ------------------------------------------------------------------ #
@app.route("/api/patients", methods=["POST", "OPTIONS"])
@api
def add_patient():
    if request.method == "OPTIONS":
        return {}
    d = body()
    ok, result = blockchain.add_patient_record(
        d["patient_id"], d["name"], d["age"], d["blood_type"],
        d.get("requester", "DiagnosticCenter")
    )
    return {"success": ok, "result": result}

@app.route("/api/patients/<patient_id>", methods=["GET"])
@api
def get_patient(patient_id):
    record = blockchain.get_patient(patient_id)
    if record:
        return {"success": True, "result": record}
    return {"success": False, "result": "Patient not found."}

@app.route("/api/patients", methods=["GET"])
@api
def list_patients():
    return {"success": True, "result": list(blockchain.patient_records.values())}

# ------------------------------------------------------------------ #
#  Diagnostic Center                                                   #
# ------------------------------------------------------------------ #
@app.route("/api/test-reports", methods=["POST", "OPTIONS"])
@api
def add_test_report():
    if request.method == "OPTIONS":
        return {}
    d = body()
    ok, result = blockchain.add_test_report(
        d["patient_id"], d["report"],
        d.get("requester", "DiagnosticCenter")
    )
    return {"success": ok, "result": result}

# ------------------------------------------------------------------ #
#  Doctor Clinic                                                        #
# ------------------------------------------------------------------ #
@app.route("/api/symptoms", methods=["POST", "OPTIONS"])
@api
def update_symptoms():
    if request.method == "OPTIONS":
        return {}
    d = body()
    ok, result = blockchain.update_symptoms(
        d["patient_id"], d["symptoms"],
        d.get("requester", "DoctorClinic")
    )
    return {"success": ok, "result": result}

@app.route("/api/prescriptions", methods=["POST", "OPTIONS"])
@api
def add_prescription():
    if request.method == "OPTIONS":
        return {}
    d = body()
    ok, result = blockchain.add_prescription(
        d["patient_id"], d["prescription"],
        d.get("requester", "DoctorClinic")
    )
    return {"success": ok, "result": result}

# ------------------------------------------------------------------ #
#  Pharmacy                                                            #
# ------------------------------------------------------------------ #
@app.route("/api/prescriptions/<patient_id>", methods=["GET"])
@api
def get_prescriptions(patient_id):
    requester = request.args.get("requester", "Pharmacy")
    ok, result = blockchain.get_prescription(patient_id, requester)
    return {"success": ok, "result": result}

# ------------------------------------------------------------------ #
#  Ledger                                                              #
# ------------------------------------------------------------------ #
@app.route("/api/chain", methods=["GET"])
@api
def get_chain():
    return {"success": True, "result": blockchain.get_chain()}

@app.route("/api/transactions", methods=["GET"])
@api
def get_transactions():
    return {"success": True, "result": blockchain.get_all_transactions()}

@app.route("/api/wallets", methods=["GET"])
@api
def get_wallets():
    return {"success": True, "result": blockchain.get_wallets()}

@app.route("/api/validate", methods=["GET"])
@api
def validate():
    return {"success": True, "result": {"valid": blockchain.is_valid()}}

@app.route("/api/stats", methods=["GET"])
@api
def stats():
    return {
        "success": True,
        "result": {
            "blocks": len(blockchain.chain),
            "patients": len(blockchain.patient_records),
            "transactions": sum(len(b.transactions) for b in blockchain.chain),
            "wallets": blockchain.get_wallets(),
            "valid": blockchain.is_valid()
        }
    }

if __name__ == "__main__":
    print("\n" + "="*60)
    print("  MEDICAL BLOCKCHAIN WEB SERVER")
    print("  Access from any machine on your network:")
    import socket
    hostname = socket.gethostname()
    try:
        local_ip = socket.gethostbyname(hostname)
    except:
        local_ip = "0.0.0.0"
    print(f"  → http://localhost:5000")
    print(f"  → http://{local_ip}:5000")
    print("="*60 + "\n")
    app.run(host="0.0.0.0", port=port, debug=False, threaded=True)
