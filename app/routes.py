import json
import requests
import os
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    # Extract data from the event
    body = json.loads(event['body']) if 'body' in event else event

    # Get parameters from the Slack request payload
    text = body.get("text", "")
    user = body.get("user_name", "unknown_user")

    # Parse job_name and server
    try:
        job_name, server = text.split()
    except ValueError:
        return {
            "statusCode": 400,
            "body": json.dumps({"response_type": "ephemeral", "text": "Please provide both job name and server in the format: `job_name server`"})
        }

    # Update job_name based on specific conditions
    if job_name == "db":
        job_name = "UpdateDatabaseFromProduction"
    elif job_name == "sdb":
        job_name = "UpdateDatabaseFromSpragueProd"
    elif job_name == "stagingdb":
        job_name = "UpdateDatabaseFromStaging"

    # List of valid servers
    valid_servers = ["fe", "bo", "jl", "staging", "3l", "test", "develop", "qa", "iit", "asset", "avenger", "kanban", "staging-sprague", "demo", "uat"]

    # Validate server
    if server not in valid_servers:
        return {
            "statusCode": 400,
            "body": json.dumps({"response_type": "ephemeral", "text": f"Invalid server name. Choose from: {', '.join(valid_servers)}"})
        }

    # Jenkins Configuration
    BASE_URL = os.environ.get("JENKINS_BASE_URL", "http://34.224.215.229:8080/buildByToken/buildWithParameters?")
    TOKEN = os.environ.get("JENKINS_TOKEN", "your-jenkins-token")
    jenkins_url = f"{BASE_URL}token={TOKEN}&job={job_name}&DESTINATION_APP=fp-{server}"

    # Trigger Jenkins Job
    try:
        response = requests.get(jenkins_url, timeout=30)
        if response.status_code == 201:
            return {
                "statusCode": 201,
                "body": json.dumps({"response_type": "in_channel", "text": f"Jenkins job '{job_name}' for server '{server}' triggered successfully by {user}!"})
            }
        else:
            logger.error(f"Failed to trigger Jenkins job. Status code: {response.status_code}")
            return {
                "statusCode": response.status_code,
                "body": json.dumps({"response_type": "ephemeral", "text": f"Failed to trigger Jenkins job. Status code: {response.status_code}"})
            }
    except requests.exceptions.RequestException as e:
        logger.error(f"Error triggering Jenkins job: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({"response_type": "ephemeral", "text": f"Error triggering Jenkins job: {str(e)}"})
        }