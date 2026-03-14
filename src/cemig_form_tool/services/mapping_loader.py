"""Loads field mapping configurations from YAML/JSON."""

from __future__ import annotations

import json
from pathlib import Path

from cemig_form_tool.models.schemas import FieldMapping


class MappingLoader:
    def load(self, path: Path) -> list[FieldMapping]:
        if path.suffix.lower() == ".json":
            payload = json.loads(path.read_text(encoding="utf-8"))
        else:
            try:
                import yaml
            except ModuleNotFoundError as exc:  # pragma: no cover
                raise RuntimeError("PyYAML is required for YAML mapping files") from exc
            payload = yaml.safe_load(path.read_text(encoding="utf-8"))
        return [FieldMapping(**item) for item in payload.get("mappings", [])]
