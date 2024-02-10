import datetime
import os

from dateutil.relativedelta import relativedelta
from prettytable import PrettyTable

from cost_explorer.modules.types import Cost, DayCount, ServiceBudget


def build_table_display(
    service_budgets_yen: dict[str, ServiceBudget],
    cost: Cost,
    start_datetime: datetime.datetime,
    end_datetime: datetime.datetime,
) -> PrettyTable:
    """Compares budgeted costs to actual costs for given services."""
    table = PrettyTable()
    table.field_names = [
        "Service",
        "Budget (Yen)",
        "Actual (Yen)",
        "Difference (Yen)",
        "Change Rate (%)",
    ]
    table.align = "r"

    end_of_month = (
        end_datetime.replace(day=1) + relativedelta(months=1)
    ) - relativedelta(days=1)
    weight = calc_weight(start_datetime, end_datetime) / calc_weight(
        start_datetime, end_of_month
    )

    for service_name, service_budget in service_budgets_yen.items():
        budget_yen = service_budget["budget_yen"]
        current_budget_yen = budget_yen * weight
        actual_usd = cost.services_cost.get(service_name, cost.total_cost)
        actual_yen = convert_to_yen(actual_usd)
        difference_yen = actual_yen - current_budget_yen
        change_rate = (
            difference_yen / current_budget_yen * 100 if current_budget_yen else 0
        )

        table.add_row(
            [
                service_budget["display_name"],
                f"{round(current_budget_yen):,}",
                f"{round(actual_yen):,}",
                f"{round(difference_yen):,}",
                f"{change_rate:,.2f}",
            ]
        )

    return table


def convert_to_yen(dollars: float) -> float:
    return dollars * float(os.environ.get("USD_TO_YEN", 150))


def count_days(
    start_datetime: datetime.datetime, end_datetime: datetime.datetime
) -> DayCount:
    business_days = 0
    holiday_days = 0
    while start_datetime <= end_datetime:
        if start_datetime.weekday() < 5:
            business_days += 1
        else:
            holiday_days += 1
        start_datetime += datetime.timedelta(days=1)
    return DayCount(business_days, holiday_days)


def calc_weight(
    start_datetime: datetime.datetime, end_datetime: datetime.datetime
) -> float:
    business_days, holiday_days = count_days(start_datetime, end_datetime)
    return business_days + holiday_days * 0.25
