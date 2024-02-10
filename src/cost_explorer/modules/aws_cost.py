import os
from datetime import datetime

from cost_explorer.modules.types import (
    Cost,
    CostExplorerClientProtocol,
    GetCostAndUsageResponse,
    TagFilter,
)


def get_costs(
    client: CostExplorerClientProtocol, start_datetime: datetime, end_datetime: datetime
) -> Cost:
    tag_filter: TagFilter = {
        "Tags": {
            "Key": os.environ["COST_EXPLORER_TAG_KEY"],
            "Values": os.environ["COST_EXPLORER_TAG_VALUES"].split(","),
        }
    }
    response: GetCostAndUsageResponse = client.get_cost_and_usage(
        TimePeriod={
            "Start": start_datetime.strftime("%Y-%m-%d"),
            "End": end_datetime.strftime("%Y-%m-%d"),
        },
        Granularity="MONTHLY",
        Metrics=["UnblendedCost"],
        GroupBy=[{"Type": "DIMENSION", "Key": "SERVICE"}],
        Filter=tag_filter,
    )
    total_cost = sum(
        float(group["Metrics"]["UnblendedCost"]["Amount"])
        for group in response["ResultsByTime"][-1]["Groups"]
    )
    services_cost = {
        group["Keys"][0]: float(group["Metrics"]["UnblendedCost"]["Amount"])
        for group in response["ResultsByTime"][-1]["Groups"]
    }
    return Cost(total_cost, services_cost)
