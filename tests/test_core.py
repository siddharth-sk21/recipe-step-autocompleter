import pytest

from app.core import (
    NGramModel,
    compile_corpus,
    milestone_1,
    milestone_2,
    milestone_3,
    tokenize,
)


def test_tokenize_normalizes_case_and_punctuation():
    assert tokenize(" Mix  Flour! ") == ["mix", "flour"]


def test_compile_corpus_discards_empty_instructions():
    assert compile_corpus(["Mix flour", "", "  "]) == [["mix", "flour"]]


def test_milestone_1_compiles_the_default_recipe_corpus():
    corpus = milestone_1()
    assert len(corpus) >= 5
    assert all(corpus)
    assert all(token == token.lower() for instruction in corpus for token in instruction)


def test_milestone_2_counts_bigrams_and_smooths_probabilities():
    model = NGramModel([["add", "salt"], ["add", "pepper"]], n=2, alpha=1.0)

    assert model.counts[("<s>",)][ "add" ] == 2
    assert model.counts[("add",)][ "salt" ] == 1
    assert model.counts[("add",)][ "pepper" ] == 1

    total = sum(model.probability(word, ["add"]) for word in model.vocabulary)
    assert total < 1.0
    assert model.probability("unknown", ["add"]) > 0


def test_milestone_2_returns_ranked_predictions():
    model = milestone_2([["add", "salt"], ["add", "salt"], ["add", "pepper"]], n=2)
    predictions = model.predict_next("add", limit=2)

    assert predictions[0][0] == "salt"
    assert predictions[0][1] > predictions[1][1]


@pytest.mark.parametrize("kwargs", [{"n": 0}, {"alpha": 0}, {"alpha": -1}])
def test_milestone_2_rejects_invalid_model_settings(kwargs):
    with pytest.raises(ValueError):
        NGramModel([["add", "salt"]], **kwargs)


def test_milestone_3_generates_a_deterministic_continuation():
    model = milestone_2([["add", "salt"], ["add", "pepper"]], n=2)

    continuation = milestone_3(
        "add",
        max_words=2,
        model=model,
    )

    assert continuation.startswith("add ")
    assert len(continuation.split()) <= 3


def test_milestone_3_sampling_is_repeatable_with_a_seed():
    model = milestone_2(
        [
            ["heat", "oil"],
            ["heat", "oil"],
            ["heat", "water"],
        ],
        n=2,
    )

    first = milestone_3("heat", max_words=3, sample=True, seed=42, model=model)
    second = milestone_3("heat", max_words=3, sample=True, seed=42, model=model)

    assert first == second


def test_milestone_3_rejects_invalid_word_limits():
    model = milestone_2([["add", "salt"]], n=2)

    with pytest.raises(ValueError):
        milestone_3("add", max_words=0, model=model)
