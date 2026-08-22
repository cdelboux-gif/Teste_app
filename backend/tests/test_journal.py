import pytest
from pydantic import ValidationError

from app.journal import JournalCreate


def test_valid_journal_entry():
    entry = JournalCreate(title="Meu dia", content="Hoje me senti mais tranquilo.", mood_label="calmo")
    assert entry.mood_label == "calmo"


def test_empty_journal_content_is_rejected():
    with pytest.raises(ValidationError):
        JournalCreate(content="")


def test_journal_content_has_size_limit():
    with pytest.raises(ValidationError):
        JournalCreate(content="x" * 10001)
