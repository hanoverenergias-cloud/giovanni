"""Application settings loaded from environment."""

from pathlib import Path

try:  # pragma: no cover
    from pydantic import Field
    from pydantic_settings import BaseSettings, SettingsConfigDict
except ModuleNotFoundError:  # pragma: no cover
    class BaseSettings:
        def __init__(self, **kwargs):
            for k, v in kwargs.items():
                setattr(self, k, v)

    def Field(default=None, **kwargs):
        return default

    def SettingsConfigDict(**kwargs):
        return kwargs


class AppSettings(BaseSettings):
    """Runtime configuration for the CEMIG form assistant."""

    model_config = SettingsConfigDict(env_prefix="CEMIG_", env_file=".env", extra="ignore")

    log_level: str = Field(default="INFO")
    confidence_threshold: float = Field(default=0.75)
    templates_dir: Path = Field(default=Path("templates"))
    outputs_dir: Path = Field(default=Path("outputs"))
    mapping_file: Path = Field(default=Path("configs/field_mapping.json"))


settings = AppSettings()
