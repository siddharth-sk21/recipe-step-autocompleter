"""These pass on day one. They check the plumbing so you notice quickly if you break it."""
import os

import pytest

from app import llm
from app.storage import Store


def test_the_store_keeps_what_you_put_in_it(tmp_path):
    store = Store(str(tmp_path / "app.json"))
    store.put("hello", {"n": 1})
    assert store.get("hello") == {"n": 1}
    assert store.get("missing", "fallback") == "fallback"
    assert store.all() == {"hello": {"n": 1}}


def test_model_settings_default_to_a_local_ollama(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)                  # no .env here
    for name in ("LLM_BASE_URL", "LLM_API_KEY", "LLM_MODEL"):
        monkeypatch.delenv(name, raising=False)
    base, key, model = llm.settings()
    assert base == "http://localhost:11434/v1" and key == "" and model == ""


def test_the_command_line_runs(capsys):
    from app.cli import main
    main(["hello"])
    assert "is ready" in capsys.readouterr().out


def test_the_suggest_command_shows_words(capsys):
    from app.cli import main
    main(["suggest", "add", "the", "--count", "3"])
    output = capsys.readouterr().out
    assert output
    assert "\t" in output


def test_the_generate_command_prints_a_continuation(capsys):
    from app.cli import main
    main(["generate", "heat", "--count", "3", "--seed", "42"])
    output = capsys.readouterr().out.strip()
    assert output


def test_the_complete_command_accepts_an_automatic_choice(capsys):
    from app.cli import main
    main(["complete", "add", "the", "--count", "3", "--steps", "2", "--choose", "1"])
    output = capsys.readouterr().out
    assert "Current step:" in output
    assert "Final step:" in output


def test_suggest_rejects_a_zero_count(capsys):
    from app.cli import main
    with pytest.raises(SystemExit):
        main(["suggest", "add", "the", "--count", "0"])

