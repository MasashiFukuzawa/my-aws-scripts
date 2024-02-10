import datetime
import os

import boto3
from dotenv import load_dotenv

from cost_explorer.modules.aws_cost import get_costs
from cost_explorer.modules.display import build_table_display
from cost_explorer.modules.slack_notification import send_slack_message_via_webhook
from cost_explorer.modules.types import ServiceBudget

load_dotenv()

client = boto3.client("ce")

now = datetime.datetime.now()
yesterday = now - datetime.timedelta(days=1)
start_of_month = yesterday.replace(day=1)

cost = get_costs(client, start_of_month, yesterday)


service_budgets: dict[str, ServiceBudget] = {
    "Amazon Elastic Compute Cloud - Compute": {
        "display_name": "EC2",
        "budget_yen": 1000,
    },
    "Amazon Simple Storage Service": {
        "display_name": "S3",
        "budget_yen": 2000,
    },
    "Total": {
        "display_name": "Total",
        "budget_yen": 3000,
    },
}

table = build_table_display(
    service_budgets,
    cost,
    start_of_month,
    yesterday,
)

message = f"{start_of_month.date().strftime('%Y/%m/%d')} ~ {yesterday.date().strftime('%Y/%m/%d')} の予実の比較結果は以下の通りです。\n為替レートは{float(os.environ.get('USD_TO_YEN', 150))}円/ドルで計算しています。"
code = table.get_string()
print(message)
print(code)

send_slack_message_via_webhook(os.environ["SLACK_WEBHOOK_URL"], message, code)
print("Slack通知が完了しました。")
