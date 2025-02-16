from app import app
from flask import jsonify, request
import requests
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Retrieve constants from .env file
TOKEN = os.getenv("TOKEN")
BASE_URL = os.getenv("BASE_URL", "http://34.224.215.229:8080/buildByToken/buildWithParameters?")

print(f"🔗 Jenkins URL: {BASE_URL}")
print(f"🔗 Jenkins Token: {TOKEN}")
# List of valid servers
VALID_SERVERS = {
    "fe", "bo", "jl", "staging", "3l", "test", "develop", "qa", "iit", "asset",
    "avenger", "kanban", "staging-sprague", "demo", "uat"
}

# Job name mappings
JOB_MAPPINGS = {
    "db": "UpdateDatabaseFromProduction",
    "sdb": "UpdateDatabaseFromSpragueProd",
    "stagingdb": "UpdateDatabaseFromStaging"
}

@app.route("/test", methods=["POST"])
def test_route():
    print("📥 Incoming request data:", request.form) 

    # Extract data from Slack payload
    data = request.form
    text = data.get("text", "").strip()  # Get the text from Slack command
    user = data.get("user_name", "Unknown User")  # Get the Slack username

    # Validate input format
    if not text:
        return jsonify({"response_type": "ephemeral", "text": "❌ *Error:* Please provide both `job_name` and `server` in the format: `job_name server`"}), 400

    try:
        job_name, server = text.split()
    except ValueError:
        return jsonify({"response_type": "ephemeral", "text": "❌ *Error:* Invalid format. Use `/command job_name server`"}), 400

    # Normalize job name and server
    job_name = JOB_MAPPINGS.get(job_name.lower(), job_name)  # Map job if needed
    server = server.lower()  # Make server case-insensitive

    # Validate server
    if server not in VALID_SERVERS:
        return jsonify({"response_type": "ephemeral", "text": f"❌ *Error:* Invalid server name.\n\n✅ *Valid servers:* `{', '.join(VALID_SERVERS)}`"}), 400

    # Construct Jenkins job URL
    jenkins_url = f"{BASE_URL}token={TOKEN}&job={job_name}&DESTINATION_APP=fp-{server}"
    print(f"🔗 Jenkins URL: {jenkins_url}")
    print(f"👤 {user} triggered Jenkins job: {job_name} on server: {server}")

    try:
        # Trigger Jenkins job
        response = requests.get(jenkins_url, timeout=30)
        response.raise_for_status()  # Raise exception for HTTP errors

        if response.status_code == 201:
            return jsonify({"response_type": "in_channel", "text": f"✅ *Success:* Jenkins job `{job_name}` for server `{server}` triggered by *{user}*!"}), 201
        else:
            return jsonify({"response_type": "ephemeral", "text": f"⚠️ *Warning:* Jenkins job triggered but returned unexpected status: `{response.status_code}`"}), response.status_code

    except requests.exceptions.RequestException as e:
        print(f"❌ Error triggering Jenkins job: {e}")
        return jsonify({"response_type": "ephemeral", "text": f"❌ *Error:* Failed to trigger Jenkins job. Please check logs.\n\n🔍 _Details:_ `{str(e)}`"}), 500
