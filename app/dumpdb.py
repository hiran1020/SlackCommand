import logging
import os
import requests
from threading import Thread
from flask import Flask, jsonify, request
import time

# Initialize Flask application
app = Flask(__name__)

# Enable logging
logging.basicConfig(level=logging.DEBUG)
app.logger.setLevel(logging.DEBUG)

# Load environment variables
TOKEN = os.getenv("TOKEN")
STGTOKEN = os.getenv("STGTOKEN")
SPRTOKEN = os.getenv("SPRTOKEN")
BASE_URL = os.getenv("BASE_URL")

# Verify base URL and tokens are loaded correctly
app.logger.debug(f"BASE_URL: {BASE_URL}")
app.logger.debug(f"TOKEN: {TOKEN[:5]}****")
app.logger.debug(f"STGTOKEN: {STGTOKEN[:5]}****")
app.logger.debug(f"SPRTOKEN: {SPRTOKEN[:5]}****")

# Valid server list
VALID_SERVERS = {"fe", "bo", "jl", "staging", "3l", "test", "develop", "qa", "iit", "asset",
                 "avenger", "kanban", "staging-sprague", "demo", "uat"}

# Job mappings
JOB_MAPPINGS = {
    "db": "UpdateDatabaseFromProduction",
    "sdb": "UpdateDatabaseFromSpragueProd",
    "stagingdb": "UpdateDatabaseFromStaging"
}

# Token mappings based on the job
TOKEN_MAPPINGS = {
    "UpdateDatabaseFromStaging": STGTOKEN,  # Use STGTOKEN for staging
    "UpdateDatabaseFromSpragueProd": SPRTOKEN,  # Use SPRTOKEN for Sprague
}

def trigger_jenkins(job_name, server, user):
    """Trigger Jenkins job asynchronously and log response time."""
    token = TOKEN_MAPPINGS.get(job_name, TOKEN)
    jenkins_url = f"{BASE_URL}token={token}&job={job_name}&DESTINATION_APP=fp-{server}"
    
    # Log request start
    app.logger.debug(f"🔗 Triggering Jenkins job {job_name} on {server} with token {token[:5]}...")

    start_time = time.time()
    try:
        response = requests.get(jenkins_url, timeout=30)
        response.raise_for_status()
        duration = round(time.time() - start_time, 2)
        
        # Log successful job triggering
        app.logger.debug(f"✅ Jenkins job triggered successfully in {duration}s")
    except requests.exceptions.RequestException as e:
        # Log the error if the request fails
        app.logger.error(f"❌ Jenkins error: {e}")

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

    # Return a response immediately to Slack
    response = {"response_type": "in_channel", "text": f"⏳ *Processing:* Jenkins job `{job_name}` on `{server}` triggered by *{user}*..."}
    
    # Trigger Jenkins in the background
    Thread(target=trigger_jenkins, args=(job_name, server, user), daemon=True).start()

    return jsonify(response), 200
