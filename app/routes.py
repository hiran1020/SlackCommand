from app import app
from flask import jsonify


@app.route("/runjenkins", methods=["POST"])
def slack_command():
    try:
        return jsonify({
	"type": "modal",
	"title": {
		"type": "plain_text",
		"text": "My App",
		"emoji": True
	},
	"submit": {
		"type": "plain_text",
		"text": "Submit",
		"emoji": True
	},
	"close": {
		"type": "plain_text",
		"text": "Cancel",
		"emoji": True
	},
	"blocks": [
		{
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": "Hello, Assistant to the Run the jobs in Jenkins servers "
			}
		},
		{
			"type": "divider"
		},
		{
			"type": "divider"
		},
		{
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": "Select the job you want to start"
			},
			"accessory": {
				"type": "multi_static_select",
				"placeholder": {
					"type": "plain_text",
					"text": "Select options",
					"emoji": True
				},
				"options": [
					{
						"text": {
							"type": "plain_text",
							"text": "*Automation e2e*",
							"emoji": True
						},
						"value": "value-0"
					},
					{
						"text": {
							"type": "plain_text",
							"text": "*DB dump of production*",
							"emoji": True
						},
						"value": "value-1"
					},
					{
						"text": {
							"type": "plain_text",
							"text": "*DB dump of Sprague Production*",
							"emoji": True
						},
						"value": "value-2"
					}
				],
				"action_id": "multi_static_select-action"
			}
		}
	]
})
    except Exception as e:
        return jsonify({
            "response_type": "ephemeral",
            "text": f"Error occurred: {str(e)}"
        })
    


