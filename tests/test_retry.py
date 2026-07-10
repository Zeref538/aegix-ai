"""Retry helper: transient API errors retry, everything else propagates."""

import httpx
import pytest
from openai import BadRequestError, RateLimitError

from app import retry as retry_mod
from app.retry import with_retry


@pytest.fixture(autouse=True)
def no_sleep(monkeypatch):
    monkeypatch.setattr(retry_mod.time, "sleep", lambda _: None)


def _rate_limit() -> RateLimitError:
    request = httpx.Request("POST", "https://example.invalid")
    response = httpx.Response(429, request=request)
    return RateLimitError("slow down", response=response, body=None)


def _bad_request() -> BadRequestError:
    request = httpx.Request("POST", "https://example.invalid")
    response = httpx.Response(400, request=request)
    return BadRequestError("nope", response=response, body=None)


def test_returns_value_without_error():
    assert with_retry(lambda: 42) == 42


def test_retries_transient_then_succeeds():
    calls = {"n": 0}

    def flaky():
        calls["n"] += 1
        if calls["n"] < 3:
            raise _rate_limit()
        return "ok"

    assert with_retry(flaky) == "ok"
    assert calls["n"] == 3


def test_gives_up_after_attempts():
    calls = {"n": 0}

    def always_fails():
        calls["n"] += 1
        raise _rate_limit()

    with pytest.raises(RateLimitError):
        with_retry(always_fails, attempts=3)
    assert calls["n"] == 3


def test_does_not_retry_non_transient_errors():
    calls = {"n": 0}

    def bad():
        calls["n"] += 1
        raise _bad_request()

    with pytest.raises(BadRequestError):
        with_retry(bad)
    assert calls["n"] == 1, "a 400 is a bug, not a blip — must not retry"
