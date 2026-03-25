from dataclasses import dataclass
from typing import Type


@dataclass
class ModelMetadata:
    name: str
    description: str
    fees: float
    date_range_type: str
    start_day: int | None = None
    end_day: int | None = None


_MODELS: dict[str, tuple[Type, ModelMetadata]] = {}


def register(
    name: str,
    description: str = "",
    fees: float = 0.0,
    date_range_type: str = "full_month",
    start_day: int | None = None,
    end_day: int | None = None,
):
    def decorator(cls):
        _MODELS[name] = (
            cls,
            ModelMetadata(
                name=name,
                description=description,
                fees=fees,
                date_range_type=date_range_type,
                start_day=start_day,
                end_day=end_day,
            ),
        )
        return cls
    return decorator


def get_model(name: str):
    return _MODELS.get(name, (None, None))[0]


def get_metadata(name: str):
    return _MODELS.get(name, (None, None))[1]


def list_models() -> list[str]:
    return sorted(_MODELS.keys())
