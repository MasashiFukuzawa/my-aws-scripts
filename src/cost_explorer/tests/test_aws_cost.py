import os
from datetime import datetime
from unittest.mock import patch

import pytest

from cost_explorer.modules.aws_cost import get_costs
from cost_explorer.modules.types import Cost


@pytest.fixture
def mock_ce_client():
    with patch("cost_explorer.modules.types.CostExplorerClientProtocol") as mock_client:
        yield mock_client


@pytest.fixture
def setup_env_vars():
    os.environ["COST_EXPLORER_TAG_KEY"] = "Project"
    os.environ["COST_EXPLORER_TAG_VALUES"] = "ProjectX,ProjectY"
    yield
    os.environ.pop("COST_EXPLORER_TAG_KEY")
    os.environ.pop("COST_EXPLORER_TAG_VALUES")


def test_get_costs(mock_ce_client, setup_env_vars):
    mock_response = {
        "ResultsByTime": [
            {
                "Groups": [
                    {
                        "Keys": ["Service1"],
                        "Metrics": {
                            "UnblendedCost": {"Amount": "100.0", "Unit": "USD"}
                        },
                    },
                    {
                        "Keys": ["Service2"],
                        "Metrics": {
                            "UnblendedCost": {"Amount": "200.0", "Unit": "USD"}
                        },
                    },
                ]
            }
        ]
    }
    mock_ce_client.get_cost_and_usage.return_value = mock_response

    result = get_costs(mock_ce_client, datetime(2022, 1, 1), datetime(2022, 1, 31))

    assert isinstance(result, Cost)
    assert result.total_cost == 300.0
    assert result.services_cost == {"Service1": 100.0, "Service2": 200.0}
