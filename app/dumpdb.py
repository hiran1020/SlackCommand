import os
import time
import requests
from threading import Thread
from flask import Flask, jsonify, request

app = Flask(__name__)

# Load environment variables
TOKEN = os.getenv("TOKEN")
STGTOKEN = os.getenv("STGTOKEN")
SPRTOKEN = os.getenv("SPRTOKEN")
BASE_URL = os.getenv("BASE_URL")
print(BASE_URL)
print(TOKEN)
print(STGTOKEN)
print(SPRTOKEN)

VALID_SERVERS = {"fe", "bo", "jl", "staging", "3l", "test", "develop", "qa", "iit", "asset",
                 "avenger", "kanban", "staging-sprague", "demo", "uat"}

JOB_MAPPINGS = {
    "db": "UpdateDatabaseFromProduction",
    "sdb": "UpdateDatabaseFromSpragueProd",
    "stagingdb": "UpdateDatabaseFromStaging"
}


TOKEN_MAPPINGS = {
    "UpdateDatabaseFromStaging": STGTOKEN,  # Use STGTOKEN for staging
    "UpdateDatabaseFromSpragueProd": SPRTOKEN,  # Use SPRTOKEN for Sprague
}


def trigger_jenkins(job_name, server, user):
    """Trigger Jenkins job asynchronously and log response time."""
    token = TOKEN_MAPPINGS.get(job_name, TOKEN)
    jenkins_url = f"{BASE_URL}token={token}&job={job_name}&DESTINATION_APP=fp-{server}"

    print(f"🔗 Triggering: {jenkins_url}")

    start_time = time.time()
    try:
        response = requests.get(jenkins_url, timeout=30)
        response.raise_for_status()
        duration = round(time.time() - start_time, 2)
        print(f"✅ {user} triggered `{job_name}` on `{server}` (Time: {duration}s)")
    except requests.exceptions.RequestException as e:
        print(f"❌ Jenkins error: {e}")


@app.route("/test", methods=["POST"])
@app.route("/test", methods=["POST"])
def test_route():
    """Slack command handler"""
    data = request.json or request.form  # Handle both JSON & form data

    # ✅ Handle Slack URL verification
    if "challenge" in data:
        return jsonify({"challenge": data["challenge"]})  # Respond to Slack's verification

    text = data.get("text", "").strip()
    user = data.get("user_name", "Unknown User")

    if not text:
        return jsonify({"response_type": "ephemeral", "text": "❌ *Error:* Provide `job_name server`."}), 400

    try:
        job_name, server = text.split()
    except ValueError:
        return jsonify({"response_type": "ephemeral", "text": "❌ *Error:* Invalid format. Use `/command job_name server`"}), 400

    job_name = JOB_MAPPINGS.get(job_name.lower(), job_name)
    server = server.lower()

    if server not in VALID_SERVERS:
        return jsonify({"response_type": "ephemeral", "text": f"❌ *Error:* Invalid server `{server}`. Valid servers: `{', '.join(VALID_SERVERS)}`"}), 400

    # ✅ Log and return response ASAP
    print(f"⚡ Received command: {user} → `{job_name}` on `{server}`")
    Thread(target=trigger_jenkins, args=(job_name, server, user), daemon=True).start()

    return jsonify({"response_type": "in_channel", "text": f"⏳ Processing `{job_name}` on `{server}`..."}), 200
