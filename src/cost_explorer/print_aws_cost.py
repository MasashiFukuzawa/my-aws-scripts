import datetime
import os

import boto3
from dateutil.relativedelta import relativedelta
from dotenv import load_dotenv
from prettytable import PrettyTable


# Function to get total and service-specific costs for a given time period, filtered by specified projects
def get_costs(start_date, end_date):
    # Define the filter for the projects
    tag_filter = {
        "Tags": {
            # e.g. "Key": "Project", "Values": ["Project1", "Project2"]
            "Key": os.environ["COST_EXPLORER_TAG_KEY"],
            "Values": os.environ["COST_EXPLORER_TAG_VALUES"].split(","),
        }
    }
    response = client.get_cost_and_usage(
        TimePeriod={
            "Start": start_date.strftime("%Y-%m-%d"),
            "End": end_date.strftime("%Y-%m-%d"),
        },
        Granularity="MONTHLY",
        Metrics=["UnblendedCost"],
        GroupBy=[{"Type": "DIMENSION", "Key": "SERVICE"}],
        Filter=tag_filter,  # Apply the tag filter
    )
    total_cost = sum(
        float(group["Metrics"]["UnblendedCost"]["Amount"])
        for group in response["ResultsByTime"][-1]["Groups"]
    )
    services_cost = {
        group["Keys"][0]: float(group["Metrics"]["UnblendedCost"]["Amount"])
        for group in response["ResultsByTime"][-1]["Groups"]
    }
    return total_cost, services_cost


# Calculate and print top 5 services based on total cost with comparison, include change rate, and move total to the top
def print_top_services_comparison(
    services_cost_last_month,
    services_cost_current,
    total_cost_last_month,
    total_cost_current,
):
    # Merge the two dictionaries and initialize a new dictionary for comparison
    all_services = {**services_cost_last_month, **services_cost_current}
    comparison_dict = {
        service: {"last_month": 0, "current_month": 0}
        for service in all_services.keys()
    }

    # Fill the comparison dictionary with actual values
    for service in comparison_dict:
        if service in services_cost_last_month:
            comparison_dict[service]["last_month"] = services_cost_last_month[service]
        if service in services_cost_current:
            comparison_dict[service]["current_month"] = services_cost_current[service]

    # Sort the dictionary based on current month's cost and pick top 5
    top_services = sorted(
        comparison_dict.items(), key=lambda x: x[1]["current_month"], reverse=True
    )[:5]

    # Create and populate the table
    table = PrettyTable()
    table.field_names = [
        "Service (Top5のみ表示)",
        "前月 (USD)",
        "今月 (USD)",
        "変化率 (%)",
    ]
    table.align = "l"  # Align text to the left

    for service, costs in top_services:
        change_rate = (
            (costs["current_month"] - costs["last_month"]) / costs["last_month"] * 100
        )
        table.add_row(
            [
                service,
                f"{costs['last_month']:.2f}",
                f"{costs['current_month']:.2f}",
                f"{change_rate:.2f}",
            ]
        )

    # Calculate total cost change rate
    total_change_rate = (
        (total_cost_current - total_cost_last_month) / total_cost_last_month * 100
    )

    # Add total costs comparison row
    table.add_row(["...", "...", "...", "..."])
    table.add_row(
        [
            "--------------------------------------",
            "----------",
            "----------",
            "----------",
        ]
    )
    table.add_row(
        [
            "Total",
            f"{total_cost_last_month:.2f}",
            f"{total_cost_current:.2f}",
            f"{total_change_rate:.2f}",
        ]
    )

    print(table)


load_dotenv()

# AWS client for Cost Explorer
client = boto3.client("ce")

# Dates for comparison
now = datetime.datetime.now()
start_of_current_month = now.replace(day=1)
start_of_last_month = (start_of_current_month - relativedelta(months=1)).replace(day=1)
end_of_last_month_period = start_of_last_month + datetime.timedelta(days=now.day - 1)

# Get costs for the current month and the same period last month, filtered by specified projects
total_cost_current, services_cost_current = get_costs(start_of_current_month, now)
total_cost_last_month, services_cost_last_month = get_costs(
    start_of_last_month, end_of_last_month_period
)

# Calculate the percentage difference in total costs
percentage_difference = (
    ((total_cost_current - total_cost_last_month) / total_cost_last_month) * 100
    if total_cost_last_month > 0
    else 0
)

# Call the function with the top 5 services by cost for last month and current month, and total costs
print(
    f"前月比で {abs(percentage_difference):.2f}% コストが{'減少' if percentage_difference < 0 else '増加'}しています。"
)
print_top_services_comparison(
    services_cost_last_month,
    services_cost_current,
    total_cost_last_month,
    total_cost_current,
)
