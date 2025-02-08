# Backend Flask Project

This project integrates a Flask backend with Jenkins and Slack. It allows users to trigger Jenkins jobs via Slack commands.

## Setup

1. Clone the repo:
   ```bash
   git clone https://github.com/yourusername/slack-jenkins-repo.git

2. Install dependencies:
   ```bash
   pip install -r requirements.txt

3. Create a `.env` file with your Slack token:
   ```bash
   SLACK_TOKEN=<your-slack-token>
   ```

4. Run the Flask app:
   ```bash
   python run.py    
   ```

## Usage

1. Trigger a Jenkins job from Slack:
   ```bash
   /runjenkins
   ```

2. Select the Jenkins job and server from the dropdown menu.

3. Click the "Submit" button to trigger the job.

## Configuration

1. Create a `.env` file with your Slack token:
   ```bash
   SLACK_TOKEN=<your-slack-token>
   ```

2. Configure the Jenkins job URL and token in the `config.py` file:
   ```python
   jenkins_url = 'https://jenkins.yourdomain.com'
   jenkins_token = 'your-jenkins-token'
   ```
