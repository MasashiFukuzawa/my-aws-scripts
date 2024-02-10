import requests


def send_slack_message_via_webhook(webhook_url: str, message: str, code: str) -> None:
    formatted_message = f"{message}\n```{code}```"
    payload = {"text": formatted_message}
    response = requests.post(webhook_url, json=payload)
    if response.status_code != 200:
        raise ValueError(
            f"Request to Slack returned an error {response.status_code}, the response is:\n{response.text}"
        )
