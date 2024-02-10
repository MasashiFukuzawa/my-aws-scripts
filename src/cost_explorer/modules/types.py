from typing import Literal, NamedTuple, Protocol, TypedDict


class TimePeriod(TypedDict):
    Start: str
    End: str


class TagValues(TypedDict):
    Key: str
    Values: list[str]


class TagFilter(TypedDict):
    Tags: TagValues


class MetricsValue(TypedDict):
    Amount: str
    Unit: str


class Metrics(TypedDict):
    UnblendedCost: MetricsValue


class GroupBy(TypedDict):
    Type: Literal["DIMENSION", "TAG", "COST_CATEGORY"]
    Key: str


class ServiceBudget(TypedDict):
    display_name: str
    budget_yen: int


class Group(TypedDict):
    Keys: list[str]
    Metrics: Metrics


class ResultByTime(TypedDict, total=False):
    Start: str
    End: str
    Groups: list[Group]
    Total: Metrics


class GetCostAndUsageResponse(TypedDict):
    ResultsByTime: list[ResultByTime]


class Cost(NamedTuple):
    total_cost: float
    services_cost: dict[str, float]


class DayCount(NamedTuple):
    business_days: int
    holiday_days: int


class CostExplorerClientProtocol(Protocol):
    def get_cost_and_usage(  # noqa: E704
        self,
        TimePeriod: TimePeriod,
        Granularity: Literal["DAILY", "MONTHLY"],
        Metrics: list[str],
        GroupBy: list[GroupBy],
        Filter: TagFilter,
    ) -> GetCostAndUsageResponse: ...
