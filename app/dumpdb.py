from threading import Thread
from flask import Flask, jsonify, request
import requests
import os

app = Flask(__name__)

# Load environment variables
TOKEN = os.getenv("TOKEN")
BASE_URL = os.getenv("BASE_URL", "http://34.224.215.229:8080/buildByToken/buildWithParameters?")

VALID_SERVERS = {"fe", "bo", "jl", "staging", "3l", "test", "develop", "qa", "iit", "asset",
                 "avenger", "kanban", "staging-sprague", "demo", "uat"}

JOB_MAPPINGS = {
    "db": "UpdateDatabaseFromProduction",
    "sdb": "UpdateDatabaseFromSpragueProd",
    "stagingdb": "UpdateDatabaseFromStaging"
}

def trigger_jenkins(job_name, server, user):
    """Background function to trigger Jenkins job."""
    jenkins_url = f"{BASE_URL}token={TOKEN}&job={job_name}&DESTINATION_APP=fp-{server}"
    try:
        response = requests.get(jenkins_url, timeout=30)
        response.raise_for_status()
        print(f"✅ {user} triggered Jenkins job: {job_name} on {server}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Error triggering Jenkins job: {e}")

@app.route("/test", methods=["POST"])
def test_route():
    """Slack command handler"""
    data = request.form
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

    # Respond immediately to Slack
    Thread(target=trigger_jenkins, args=(job_name, server, user)).start()
    
    return jsonify({"response_type": "in_channel", "text": f"⏳ *Processing:* Jenkins job `{job_name}` on `{server}` triggered by *{user}*..."}), 200

if __name__ == "__main__":
    app.run(port=5000)
