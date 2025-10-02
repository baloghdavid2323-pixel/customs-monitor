from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

def send_slack(bot_token: str, channel: str, text: str):
    client = WebClient(token=bot_token)
    try:
        client.chat_postMessage(channel=channel, text=text)
    except SlackApiError as e:
        print(f"Slack error: {e.response['error']}")
