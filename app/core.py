"""Recipe instruction corpus preparation for Milestone 1."""

from __future__ import annotations

import re
from typing import Iterable


DEFAULT_INSTRUCTIONS = (
    "preheat the oven to 350 degrees",
    "mix the flour sugar and salt in a bowl",
    "add the eggs and stir until combined",
    "heat the oil in a large skillet",
    "add the onions and cook until soft",
    "stir in the garlic and cook for one minute",
    "season with salt and pepper",
    "bake until golden brown and serve warm",
    "let the mixture cool before serving",
)

TOKEN_RE = re.compile(r"[a-z0-9]+(?:'[a-z0-9]+)?")


def tokenize(text: str) -> list[str]:
    """Normalize an instruction into lowercase word tokens."""
    return TOKEN_RE.findall(text.lower())


def compile_corpus(instructions: Iterable[str]) -> list[list[str]]:
    """Clean recipe instructions and discard empty entries."""
    return [tokens for instruction in instructions if (tokens := tokenize(instruction))]


def milestone_1(instructions: Iterable[str] = DEFAULT_INSTRUCTIONS) -> list[list[str]]:
    """Compile and normalize a corpus of recipe instructions."""
    return compile_corpus(instructions)
