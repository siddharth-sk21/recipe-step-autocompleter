from app.core import compile_corpus, milestone_1, tokenize


def test_tokenize_normalizes_case_and_punctuation():
    assert tokenize(" Mix  Flour! ") == ["mix", "flour"]


def test_compile_corpus_discards_empty_instructions():
    assert compile_corpus(["Mix flour", "", "  "]) == [["mix", "flour"]]


def test_milestone_1_compiles_the_default_recipe_corpus():
    corpus = milestone_1()
    assert len(corpus) >= 5
    assert all(corpus)
    assert all(token == token.lower() for instruction in corpus for token in instruction)
