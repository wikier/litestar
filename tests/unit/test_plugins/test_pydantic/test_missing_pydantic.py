"""Tests for running without pydantic, which is an optional dependency."""

from __future__ import annotations

import importlib
import sys

import pytest

from litestar import Litestar, get
from litestar.exceptions import MissingDependencyException


@pytest.fixture
def without_pydantic(monkeypatch: pytest.MonkeyPatch) -> None:
    """Simulate pydantic not being installed.

    A ``None`` entry in ``sys.modules`` makes ``import pydantic`` raise ``ImportError``. The already-imported
    ``litestar.plugins.pydantic`` modules are evicted so they are imported again and hit that error.
    """
    monkeypatch.setitem(sys.modules, "pydantic", None)
    monkeypatch.setitem(sys.modules, "pydantic_core", None)
    for name in list(sys.modules):
        if name.startswith("litestar.plugins.pydantic"):
            monkeypatch.delitem(sys.modules, name)


@pytest.mark.usefixtures("without_pydantic")
def test_import_without_pydantic_raises_missing_dependency() -> None:
    with pytest.raises(MissingDependencyException, match="pydantic"):
        importlib.import_module("litestar.plugins.pydantic")


@pytest.mark.usefixtures("without_pydantic")
def test_app_without_pydantic_skips_pydantic_plugins() -> None:
    """The default pydantic plugins are optional, so an app must start without pydantic installed."""

    @get("/")
    async def handler() -> str:
        return "ok"

    app = Litestar([handler])

    assert not any(type(plugin).__module__.startswith("litestar.plugins.pydantic") for plugin in app.plugins)
