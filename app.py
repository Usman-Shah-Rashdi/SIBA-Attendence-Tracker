
import os
import secrets

from flask import Flask, jsonify, render_template, request, session

from siba_portal import (
    PortalError,
    PortalLoginError,
    SibaPortalClient,
)

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get(
    "FLASK_SECRET_KEY",
    secrets.token_hex(32),
)

clients: dict[str, SibaPortalClient] = {}


def _client() -> SibaPortalClient:
    client_id = session.get("client_id")
    if not client_id or client_id not in clients:
        raise PortalLoginError("Log in to SIBA before requesting attendance.")
    return clients[client_id]


def _error_response(error: PortalError):
    status = 401 if isinstance(error, PortalLoginError) else 502
    return jsonify({"error": str(error)}), status


@app.route("/")
def index():
    return render_template("index.html")


@app.post("/api/login")
def login():
    data = request.get_json(silent=True) or request.form
    client = SibaPortalClient(
        base_url=os.environ.get(
            "SIBA_PORTAL_URL",
            "http://sibagrades.iba-suk.edu.pk:86/",
        ),
        timeout=float(os.environ.get("SIBA_PORTAL_TIMEOUT", "20")),
    )
    try:
        client.login(data.get("username", ""), data.get("password", ""))
    except PortalError as error:
        return _error_response(error)

    client_id = secrets.token_urlsafe(24)
    clients[client_id] = client
    session["client_id"] = client_id
    return jsonify({"message": "Logged in to SIBA."})


@app.post("/api/logout")
def logout():
    client_id = session.pop("client_id", None)
    if client_id:
        clients.pop(client_id, None)
    return jsonify({"message": "Logged out."})


@app.get("/api/attendance/options")
def attendance_options():
    try:
        client = _client()
        semester = request.args.get("semester")
        return jsonify(
            client.select_semester(semester)
            if semester
            else client.options()
        )
    except PortalError as error:
        return _error_response(error)


@app.route("/api/attendance")
def attendance():
    try:
        result = _client().attendance(
            semester=request.args.get("semester"),
            subject=request.args.get("subject"),
        )
    except PortalError as error:
        return _error_response(error)

    summary = result["summary"]
    subject = result["subject"] or {"name": "Unknown subject"}
    return jsonify([{
        "subject": subject["name"],
        "attended": summary["present_units"],
        "absent": summary["absent_units"],
        "total": summary["total_units"],
        "attended_units": summary["present_units"],
        "absent_units": summary["absent_units"],
        "total_units": summary["total_units"],
        "absence_boxes_used": summary["absence_boxes_used"],
        "allowed_absence_units": summary["allowed_absence_units"],
    }])


@app.get("/api/attendance/details")
def attendance_details():
    try:
        return jsonify(_client().attendance(
            semester=request.args.get("semester"),
            subject=request.args.get("subject"),
        ))
    except PortalError as error:
        return _error_response(error)


@app.get("/api/attendance/snapshot")
def attendance_snapshot():
    try:
        semester = request.args.get("semester")
        if semester == "":
            return jsonify({"error": "Select a semester before saving."}), 400
        records = _client().all_attendance(semester_value=semester)
        return jsonify(records)
    except PortalError as error:
        return _error_response(error)
    except (KeyError, TypeError, ValueError) as error:
        app.logger.exception("Invalid attendance snapshot response")
        return jsonify({
            "error": "SIBA returned invalid data while creating the snapshot."
        }), 502


if __name__ == "__main__":
    app.run(debug=False)
