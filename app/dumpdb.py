from flask import Flask, jsonify, request
import logging
import os

app = Flask(__name__)

# Enable logging
logging.basicConfig(level=logging.DEBUG)

# Load environment variables
TOKEN = os.getenv("TOKEN")
STGTOKEN = os.getenv("STGTOKEN")
SPRTOKEN = os.getenv("SPRTOKEN")
BASE_URL = os.getenv("BASE_URL")

# Set up valid servers and job mappings
VALID_SERVERS = {"fe", "bo", "jl", "staging", "3l", "test", "develop", "qa", "iit", "asset",
                 "avenger", "kanban", "staging-sprague", "demo", "uat"}

JOB_MAPPINGS = {
    "db": "UpdateDatabaseFromProduction",
    "sdb": "UpdateDatabaseFromSpragueProd",
    "stagingdb": "UpdateDatabaseFromStaging"
}

# Slack command handler
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
    
    # Trigger Jenkins in the background (can implement threading or background task)
    # For now, just log for testing
    app.logger.debug(f"Triggered Jenkins job: {job_name} on {server} by {user}")

    return jsonify(response), 200

if __name__ == "__main__":
    app.run(debug=True)
