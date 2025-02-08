from app import app
from flask import jsonify, request
import requests
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
# Constants from .env file
TOKEN = os.getenv("TOKEN")
BASE_URL = os.getenv("BASE_URL")

@app.route("/test", methods=["POST"])
def test_route():
    
    print("Incoming request data:", request.form) 
    # Extract data from Slack payload
    data = request.form
    text = data.get("text", "")  # The arguments after the slash command
    user = data.get("user_name")  # Slack username of the person triggering the command

    # Parse the text for job_name and server (assuming format: "job_name server")
    try:
        job_name, server = text.split()
    except ValueError:
        return jsonify({"response_type": "ephemeral", "text": "Please provide both job name and server in the format: `job_name server`"}), 400

    # Construct Jenkins job URL
    jenkins_url = f"{BASE_URL}/{job_name}/buildWithParameters?token={TOKEN}&DESTINATION_APP=fp-{server}"

    print(f"{user} triggered Jenkins job: {jenkins_url}")
    
    try:
        # Trigger Jenkins job
        response = requests.post(jenkins_url, timeout=10)
        
        if response.status_code == 201:
            return jsonify({"response_type": "in_channel", "text": f"Jenkins job '{job_name}' for server '{server}' triggered successfully by {user}!"}), 201
        else:
            return jsonify({"response_type": "ephemeral", "text": f"Failed to trigger Jenkins job. Status code: {response.status_code}"}), response.status_code
    
    except requests.exceptions.RequestException as e:
        print(f"Error triggering Jenkins job: {e}")
        return jsonify({"response_type": "ephemeral", "text": f"Error triggering Jenkins job: {str(e)}"}), 500