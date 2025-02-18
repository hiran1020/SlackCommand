from flask import Blueprint, jsonify, request
import logging
import requests
import os
from dotenv import load_dotenv

# Initialize blueprint
dumpdb = Blueprint('dumpdb', __name__)

# Load environment variables from .env file
load_dotenv()

# Constants from .env file
TOKEN = os.getenv("TOKEN")
STGTOKEN = os.getenv("STGTOKEN")
SPRTOKEN = os.getenv("SPRTOKEN")
BASE_URL = os.getenv("BASE_URL", "http://34.224.215.229:8080/buildByToken/buildWithParameters?")

# Logging setup
logging.basicConfig(level=logging.DEBUG)

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

TOKEN_MAPPINGS = {
    "UpdateDatabaseFromStaging": STGTOKEN,  # Use STGTOKEN for staging
    "UpdateDatabaseFromSpragueProd": SPRTOKEN,  # Use SPRTOKEN for Sprague
}

@dumpdb.route("/hy-run", methods=["POST"])
def hy_run():
    """Handles Slack command to trigger Jenkins."""
    logging.debug(f"📩 Slack request received: {request.form}")

    data = request.form
    text = data.get("text", "").strip()
    user = data.get("user_name", "Unknown User")

    if not text:
        return jsonify({"response_type": "ephemeral", "text": "❌ *Error:* Provide `job_name server`."}), 200

    try:
        job_name, server = text.split()
    except ValueError:
        return jsonify({"response_type": "ephemeral", "text": "❌ *Error:* Invalid format. Use `/trigger job_name server`"}), 200

    job_name = JOB_MAPPINGS.get(job_name.lower(), job_name)
    server = server.lower()

    token_id = TOKEN_MAPPINGS.get(job_name)

    if server not in VALID_SERVERS:
        return jsonify({"response_type": "ephemeral", "text": f"❌ *Error:* Invalid server `{server}`."}), 200

    # Construct Jenkins job URL
    jenkins_url = f"{BASE_URL}token={token_id}&job={job_name}&DESTINATION_APP=fp-{server}"
    logging.info(f"🔹 Triggering Jenkins job: {jenkins_url}")

    try:
        response = requests.get(jenkins_url, timeout=10)
        if response.status_code == 201:
            return jsonify({"response_type": "in_channel", "text": f"✅ Jenkins job `{job_name}` triggered for `{server}` by *{user}*."}), 200
        else:
            return jsonify({"response_type": "ephemeral", "text": f"❌ Failed to trigger job. Status: {response.status_code}."}), 200
    except requests.exceptions.RequestException as e:
        logging.error(f"❌ Jenkins trigger failed: {e}")
        return jsonify({"response_type": "ephemeral", "text": f"❌ Error: {str(e)}"}), 200
