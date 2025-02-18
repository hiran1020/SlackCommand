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
app.logger.debug(f"TOKEN: {TOKEN}****")
app.logger.debug(f"STGTOKEN: {STGTOKEN}****")
app.logger.debug(f"SPRTOKEN: {SPRTOKEN}****")

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



        
@app.route("/hy-run", methods=["POST"])
def hy_run():
    """Handle /hy-run Slack command"""
    app.logger.debug(f"📩 Received Slack request: {request.form}")

    data = request.form
    text = data.get("text", "").strip()
    user = data.get("user_name", "Unknown User")

    if not text:
        return jsonify({"response_type": "ephemeral", "text": "❌ *Error:* Provide `job_name server`."}), 200

    try:
        job_name, server = text.split()
    except ValueError:
        return jsonify({"response_type": "ephemeral", "text": "❌ *Error:* Invalid format. Use `/hy-run job_name server`"}), 200

    job_name = JOB_MAPPINGS.get(job_name.lower(), job_name)
    server = server.lower()

    if server not in VALID_SERVERS:
        return jsonify({"response_type": "ephemeral", "text": f"❌ *Error:* Invalid server `{server}`."}), 200

    #    """Trigger Jenkins job asynchronously and log response time."""
    token = TOKEN_MAPPINGS.get(job_name, TOKEN)
    jenkins_url = f"{BASE_URL}token={token}&job={job_name}&DESTINATION_APP=fp-{server}"
    print("jenkins url:",jenkins_url)
    # Respond quickly to Slack
    response = {
        "response_type": "in_channel",
        "text": f"⏳ *Processing:* Jenkins job `{job_name}` on `{server}` triggered by *{user}*..."
    }
    

    return jsonify(response), 200  # <-- Immediate response
