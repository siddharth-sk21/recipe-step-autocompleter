"""Held-out evaluation for unigram, bigram, and trigram models."""

from __future__ import annotations

import csv
import json
import math
import random
from pathlib import Path
from typing import Iterable, Sequence

from .core import NGramModel, milestone_1


def split_corpus(
    corpus: Iterable[Sequence[str]],
    *,
    seed: int = 42,
    train_ratio: float = 0.8,
) -> tuple[list[list[str]], list[list[str]]]:
    """Split complete instructions into reproducible training and test corpora."""
    instructions = [list(instruction) for instruction in corpus if instruction]
    if not instructions:
        raise ValueError("corpus must contain at least one instruction")
    if not 0 < train_ratio < 1:
        raise ValueError("train_ratio must be between zero and one")

    shuffled = list(instructions)
    random.Random(seed).shuffle(shuffled)
    if len(shuffled) == 1:
        return shuffled, []

    train_size = int(len(shuffled) * train_ratio)
    train_size = max(1, min(train_size, len(shuffled) - 1))
    return shuffled[:train_size], shuffled[train_size:]


def held_out_examples(
    test_corpus: Iterable[Sequence[str]],
    n: int,
) -> list[tuple[tuple[str, ...], str]]:
    """Build (context, target) examples from held-out padded instructions."""
    if n < 1:
        raise ValueError("n must be at least 1")

    examples: list[tuple[tuple[str, ...], str]] = []
    for instruction in test_corpus:
        padded = ["<s>"] * (n - 1) + list(instruction) + ["</s>"]
        for index in range(n - 1, len(padded)):
            context = tuple(padded[index - n + 1:index])
            examples.append((context, padded[index]))
    return examples


def evaluate_model(model: NGramModel, test_corpus: Iterable[Sequence[str]]) -> dict:
    """Calculate top-1/top-5 accuracy and perplexity on held-out data."""
    examples = held_out_examples(test_corpus, model.n)
    if not examples:
        raise ValueError("test corpus must contain at least one evaluation example")

    candidates = sorted([*model.vocabulary, "</s>"])
    top1_correct = 0
    top5_correct = 0
    negative_log_likelihood = 0.0

    for context, target in examples:
        ranked = sorted(
            ((word, model.probability(word, context)) for word in candidates),
            key=lambda item: (-item[1], item[0]),
        )
        top_words = [word for word, _ in ranked]
        top1_correct += target == top_words[0]
        top5_correct += target in top_words[:5]

        probability = model.probability(target, context)
        if probability <= 0:
            raise ValueError("evaluation probability must be positive")
        negative_log_likelihood -= math.log(probability)

    example_count = len(examples)
    return {
        "model": f"{model.n}-gram",
        "n": model.n,
        "alpha": model.alpha,
        "top1_accuracy": top1_correct / example_count,
        "top5_accuracy": top5_correct / example_count,
        "perplexity": math.exp(negative_log_likelihood / example_count),
        "test_examples": example_count,
    }


def evaluate_all(
    corpus: Iterable[Sequence[str]],
    *,
    seed: int = 42,
    train_ratio: float = 0.8,
    alpha: float = 1.0,
) -> dict:
    """Train three models on the same reproducible held-out split."""
    instructions = [list(instruction) for instruction in corpus if instruction]
    train_corpus, test_corpus = split_corpus(
        instructions,
        seed=seed,
        train_ratio=train_ratio,
    )

    train_keys = {tuple(instruction) for instruction in train_corpus}
    test_keys = {tuple(instruction) for instruction in test_corpus}
    if train_keys.intersection(test_keys):
        raise RuntimeError("training and test instructions must not overlap")
    if not test_corpus:
        raise ValueError("test corpus must contain at least one instruction")

    results = []
    for n in (1, 2, 3):
        model = NGramModel(train_corpus, n=n, alpha=alpha)
        results.append(evaluate_model(model, test_corpus))

    return {
        "seed": seed,
        "train_ratio": train_ratio,
        "dataset_instructions": len(instructions),
        "train_instructions": len(train_corpus),
        "test_instructions": len(test_corpus),
        "alpha": alpha,
        "results": results,
    }


def write_evaluation(
    report: dict,
    csv_path: str | Path = "results/evaluation.csv",
    json_path: str | Path = "results/evaluation.json",
) -> tuple[Path, Path]:
    """Write evaluation metrics in both CSV and JSON formats."""
    csv_file = Path(csv_path)
    json_file = Path(json_path)
    csv_file.parent.mkdir(parents=True, exist_ok=True)
    json_file.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        "model",
        "n",
        "alpha",
        "top1_accuracy",
        "top5_accuracy",
        "perplexity",
        "test_examples",
    ]
    with csv_file.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(report["results"])

    json_file.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return csv_file, json_file


def main() -> None:
    corpus = milestone_1()
    report = evaluate_all(corpus)
    csv_path, json_path = write_evaluation(report)
    print(json.dumps(report, indent=2))
    print(f"Saved {csv_path}")
    print(f"Saved {json_path}")


if __name__ == "__main__":
    main()
