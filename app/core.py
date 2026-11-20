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
    "whisk the eggs with the milk",
    "pour the batter into the prepared pan",
    "chop the vegetables into small pieces",
    "simmer the sauce over low heat",
    "bring the water to a boil",
    "reduce the heat and cover the pot",
    "fold in the cheese gently",
    "drizzle olive oil over the vegetables",
    "knead the dough until smooth",
    "roll out the dough on a floured surface",
    "cut the cookies with a round cutter",
    "rest the dough for thirty minutes",
    "melt the butter in a saucepan",
    "cream the butter and sugar together",
    "fold the whipped cream into the mixture",
    "spread the frosting evenly over the cake",
    "slice the bread before serving",
    "toast the bread until golden",
    "rinse the rice under cold water",
    "add the stock and bring to a boil",
    "cook the pasta according to package directions",
    "drain the pasta and reserve some cooking water",
    "toss the pasta with the sauce",
    "marinate the chicken for two hours",
    "brush the chicken with oil",
    "grill the chicken until cooked through",
    "let the meat rest before slicing",
    "chill the dish for one hour",
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
        self.counts_by_order: dict[int, dict[tuple[str, ...], Counter[str]]] = {
            order: defaultdict(Counter)
            for order in range(1, n + 1)
        }
        self.context_counts_by_order: dict[int, Counter[tuple[str, ...]]] = {
            order: Counter()
            for order in range(1, n + 1)
        }
        self._count_ngrams()

    def _count_ngrams(self) -> None:
        for instruction in self.corpus:
            padded = ["<s>"] * (self.n - 1) + instruction + ["</s>"]
            for index, next_word in enumerate(padded):
                for order in range(1, self.n + 1):
                    context_length = order - 1
                    context_start = index - context_length
                    if context_start < 0:
                        continue
                    context = tuple(padded[context_start:index])
                    self.counts_by_order[order][context][next_word] += 1
                    self.context_counts_by_order[order][context] += 1

        self.counts = self.counts_by_order[self.n]
        self.context_counts = self.context_counts_by_order[self.n]

    def _probability_with_backoff(
        self,
        word: str,
        context: Sequence[str],
    ) -> tuple[float, tuple[str, ...]]:
        tokens = list(context)[-(self.n - 1):]
        candidates: list[tuple[str, ...]] = []
        for length in range(len(tokens), -1, -1):
            suffix = tokens[-length:] if length else []
            order = length + 1
            if order <= self.n:
                candidates.append(tuple(suffix))

        for key in candidates:
            order = len(key) + 1
            counts = self.counts_by_order[order].get(key)
            if counts:
                denominator = self.context_counts_by_order[order].get(key, 0)
                return (
                    (counts[word] + self.alpha)
                    / (denominator + self.alpha * (len(self.vocabulary) + 1)),
                    key,
                )

        unigram = self.counts_by_order[1].get((), Counter())
        denominator = self.context_counts_by_order[1].get((), 0)
        return (
            (unigram[word] + self.alpha)
            / (denominator + self.alpha * (len(self.vocabulary) + 1)),
            (),
        )

    def probability(self, word: str, context: Sequence[str] = ()) -> float:
        """Return a maximum-likelihood probability with add-alpha smoothing."""
        probability, _ = self._probability_with_backoff(word, context)
        return probability

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
