"""Recipe instruction corpus preparation for Milestone 1."""

from __future__ import annotations

import re
import random
from collections import Counter, defaultdict
from typing import Iterable, Sequence


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


class NGramModel:
    """Count n-grams and predict words using add-alpha smoothing."""

    def __init__(
        self,
        corpus: Iterable[Sequence[str]],
        n: int = 3,
        alpha: float = 1.0,
    ):
        if n < 1:
            raise ValueError("n must be at least 1")
        if alpha <= 0:
            raise ValueError("alpha must be greater than zero")

        self.n = n
        self.alpha = alpha
        self.corpus = [list(tokens) for tokens in corpus if tokens]
        if not self.corpus:
            raise ValueError("corpus must contain at least one instruction")

        self.vocabulary = sorted({
            token
            for instruction in self.corpus
            for token in instruction
        })
        self.counts: dict[tuple[str, ...], Counter[str]] = defaultdict(Counter)
        self.context_counts: Counter[tuple[str, ...]] = Counter()
        self._count_ngrams()

    def _count_ngrams(self) -> None:
        for instruction in self.corpus:
            padded = ["<s>"] * (self.n - 1) + instruction + ["</s>"]
            for index in range(self.n - 1, len(padded)):
                context = tuple(padded[index - self.n + 1:index])
                next_word = padded[index]
                self.counts[context][next_word] += 1
                self.context_counts[context] += 1

    def probability(self, word: str, context: Sequence[str] = ()) -> float:
        """Return a maximum-likelihood probability with add-alpha smoothing."""
        context_tokens = list(context)
        if self.n > 1:
            context_tokens = context_tokens[-(self.n - 1):]
            context_tokens = (
                ["<s>"] * (self.n - 1 - len(context_tokens)) + context_tokens
            )
        else:
            context_tokens = []

        key = tuple(context_tokens)
        possible_words = len(self.vocabulary) + 1
        return (
            self.counts[key][word] + self.alpha
        ) / (
            self.context_counts[key] + self.alpha * possible_words
        )

    def predict_next(
        self,
        prefix: str | Sequence[str],
        limit: int = 5,
    ) -> list[tuple[str, float]]:
        """Return the highest-probability next words for a prefix."""
        if limit < 1:
            raise ValueError("limit must be at least 1")

        if isinstance(prefix, str):
            context = tokenize(prefix)
        else:
            context = list(prefix)

        if self.n > 1:
            context = context[-(self.n - 1):]

        candidates = [
            (word, self.probability(word, context))
            for word in self.vocabulary
        ]
        return sorted(candidates, key=lambda item: (-item[1], item[0]))[:limit]

    def generate(
        self,
        prefix: str = "",
        max_words: int = 10,
        *,
        sample: bool = False,
        seed: int | None = None,
    ) -> str:
        """Generate a continuation by choosing smoothed next words."""
        if max_words < 1:
            raise ValueError("max_words must be at least 1")

        result = tokenize(prefix)
        rng = random.Random(seed)

        for _ in range(max_words):
            context = result[-(self.n - 1):] if self.n > 1 else []
            options = [
                (word, self.probability(word, context))
                for word in sorted([*self.vocabulary, "</s>"])
            ]

            if sample:
                words = [word for word, _ in options]
                weights = [probability for _, probability in options]
                next_word = rng.choices(words, weights=weights, k=1)[0]
            else:
                next_word = max(
                    options,
                    key=lambda item: (item[1], item[0]),
                )[0]

            if next_word == "</s>":
                break
            result.append(next_word)

        return " ".join(result)


def milestone_2(
    corpus: Iterable[Sequence[str]] | None = None,
    n: int = 3,
    alpha: float = 1.0,
) -> NGramModel:
    """Build an n-gram model from the compiled recipe corpus."""
    source = corpus if corpus is not None else milestone_1()
    return NGramModel(source, n=n, alpha=alpha)


def milestone_3(
    prefix: str = "",
    max_words: int = 10,
    *,
    sample: bool = False,
    seed: int | None = None,
    model: NGramModel | None = None,
) -> str:
    """Generate a recipe-step continuation from a partial instruction."""
    active_model = model if model is not None else milestone_2()
    return active_model.generate(
        prefix,
        max_words=max_words,
        sample=sample,
        seed=seed,
    )


def milestone_4(argv: list[str] | None = None) -> None:
    """Run the command-line interface."""
    from .cli import main

    main(argv)
