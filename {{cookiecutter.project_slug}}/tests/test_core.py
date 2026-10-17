"""Unit tests for core functionality."""

from hypothesis import given, strategies as st
from syrupy.assertion import SnapshotAssertion

from {{ cookiecutter.package_name }}.core import get_greeting
{% if cookiecutter.include_cli in [True, "yes", "true", "True", "1"] %}
from unittest.mock import patch

import pytest

import {{ cookiecutter.package_name }}
from {{ cookiecutter.package_name }} import _lazy
{% endif %}


def test_get_greeting_default() -> None:
    """Test get_greeting with empty string defaults to World."""
    assert get_greeting("") == "Hello, World!"
    assert get_greeting("   ") == "Hello, World!"


def test_get_greeting_custom(sample_name: str) -> None:
    """Test get_greeting with a specific name."""
    assert get_greeting(sample_name) == f"Hello, {sample_name}!"


def test_get_greeting_snapshot(snapshot: SnapshotAssertion) -> None:
    """Test get_greeting output matches syrupy snapshot."""
    greeting = get_greeting("Zenith")
    assert greeting == snapshot


@given(st.text())
def test_get_greeting_property(name: str) -> None:
    """Property-based test: get_greeting always returns a well-formed greeting."""
    greeting = get_greeting(name)
    assert greeting.startswith("Hello, ")
    assert greeting.endswith("!")
    clean = name.strip()
    expected = clean or "World"
    assert expected in greeting
{% if cookiecutter.include_cli in [True, "yes", "true", "True", "1"] %}


def test_lazy_accessors_dunder() -> None:
    """Test accessing dunders raises AttributeError directly."""
    with pytest.raises(AttributeError, match="has no attribute '__unknown__'"):
        _ = getattr({{ cookiecutter.package_name }}, "__unknown__")


def test_lazy_accessors_unknown_attr() -> None:
    """Test accessing unknown attributes raises AttributeError."""
    with pytest.raises(AttributeError, match="has no attribute 'nonexistent_symbol'"):
        _ = getattr({{ cookiecutter.package_name }}, "nonexistent_symbol")


def test_lazy_accessors_submodule_import_error() -> None:
    """Test re-raising ModuleNotFoundError when error is from internal dependency."""
    with (
        patch("importlib.import_module", side_effect=ModuleNotFoundError("unrelated")),
        pytest.raises(ModuleNotFoundError, match="unrelated"),
    ):
        _lazy._resolve_or_raise("{{ cookiecutter.package_name }}", "some_mod")


def test_lazy_dir_without_all_list() -> None:
    """Test module_dir when __all__ is not a list or tuple."""
    mod_globals: dict[str, object] = {"__name__": "dummy", "__all__": None, "foo": 1}
    _, mod_dir = _lazy.accessors(mod_globals, {})
    assert mod_dir() == ["__all__", "__name__", "foo"]
{% endif %}

