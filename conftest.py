"""
conftest.py — Pytest configuration for DamnCRUD test suite.

Registers the screenshoot/ directory fixture so that pytest-xdist
workers don't race to create it, and provides a shared BASE_URL
session-scoped fixture for convenience.
"""
import os
import pytest

# Ensure screenshot directory exists before any worker spawns tests
SS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "screenshoot")
os.makedirs(SS_DIR, exist_ok=True)


@pytest.fixture(scope="session")
def base_url():
    """Return the base URL under test (overridable via BASE_URL env var)."""
    return os.environ.get("BASE_URL", "http://localhost/DamnCRUD")
