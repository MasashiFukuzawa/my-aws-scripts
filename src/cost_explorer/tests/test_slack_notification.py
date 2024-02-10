import pytest
import requests_mock

from cost_explorer.modules import slack_notification


def test_send_slack_message_via_webhook_success():
    with requests_mock.Mocker() as m:
        m.post("http://mocked_url.com", status_code=200)
        slack_notification.send_slack_message_via_webhook(
            "http://mocked_url.com", "Test message", "Test code"
        )


def test_send_slack_message_via_webhook_failure():
    with requests_mock.Mocker() as m:
        m.post("http://mocked_url.com", status_code=400, text="Bad Request")
        with pytest.raises(ValueError) as e:
            slack_notification.send_slack_message_via_webhook(
                "http://mocked_url.com", "Test message", "Test code"
            )
        assert (
            str(e.value)
            == "Request to Slack returned an error 400, the response is:\nBad Request"
        )
