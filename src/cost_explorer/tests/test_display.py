import datetime

import pytest
from prettytable import PrettyTable

from cost_explorer.modules.display import (
    build_table_display,
    calc_weight,
    convert_to_yen,
    count_days,
)
from cost_explorer.modules.types import Cost


@pytest.fixture
def service_budgets_yen():
    return {
        "Amazon Elastic Compute Cloud - Compute": {
            "display_name": "EC2",
            "budget_yen": 673473,
        },
        "Amazon Simple Storage Service": {
            "display_name": "S3",
            "budget_yen": 212299,
        },
        "Total": {
            "display_name": "Total",
            "budget_yen": 2145852,
        },
    }


@pytest.fixture
def cost_obj():
    return Cost(
        services_cost={
            "Amazon Elastic Compute Cloud - Compute": 5000.25,
            "Amazon Simple Storage Service": 1500.25,
        },
        total_cost=6501.0,
    )


def test_build_table_display(service_budgets_yen, cost_obj, monkeypatch):
    monkeypatch.setenv("USD_TO_YEN", "150")
    start_datetime = datetime.datetime(2024, 1, 1)
    end_datetime = datetime.datetime(2024, 1, 31)

    result = build_table_display(
        service_budgets_yen, cost_obj, start_datetime, end_datetime
    )

    assert isinstance(result, PrettyTable)
    result_string = result.get_string()
    assert "EC2" in result_string
    assert "S3" in result_string
    assert "Total" in result_string


def test_convert_to_yen():
    dollars = 1299.2512785
    expected_yen = 194887.691775
    assert f"{convert_to_yen(dollars):.2f}" == f"{expected_yen:.2f}"


@pytest.mark.parametrize(
    "start_datetime, end_datetime, expected",
    [
        (
            datetime.datetime(2024, 1, 1),
            datetime.datetime(2024, 1, 7),
            (5, 2),
        ),
        (
            datetime.datetime(2024, 1, 8),
            datetime.datetime(2024, 1, 14),
            (5, 2),
        ),
        (
            datetime.datetime(2024, 1, 1),
            datetime.datetime(2024, 1, 31),
            (23, 8),
        ),
    ],
)
def test_count_days(start_datetime, end_datetime, expected):
    result = count_days(start_datetime, end_datetime)
    assert result.business_days == expected[0]
    assert result.holiday_days == expected[1]


@pytest.mark.parametrize(
    "start_datetime, end_datetime, expected",
    [
        (datetime.datetime(2024, 1, 1), datetime.datetime(2024, 1, 7), 5.5),
        (
            datetime.datetime(2024, 1, 8),
            datetime.datetime(2024, 1, 14),
            5.5,
        ),
        (
            datetime.datetime(2024, 1, 1),
            datetime.datetime(2024, 1, 31),
            25,
        ),
    ],
)
def test_calc_weight(start_datetime, end_datetime, expected):
    result = calc_weight(start_datetime, end_datetime)
    assert result == expected
