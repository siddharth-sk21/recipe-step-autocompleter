from app.evaluation import evaluate_all, held_out_examples, split_corpus, write_evaluation


def test_split_is_reproducible_and_keeps_instructions_separate():
    corpus = [["instruction", str(index)] for index in range(20)]

    first_train, first_test = split_corpus(corpus, seed=42)
    second_train, second_test = split_corpus(corpus, seed=42)

    assert first_train == second_train
    assert first_test == second_test
    assert set(map(tuple, first_train)).isdisjoint(set(map(tuple, first_test)))
    assert len(first_train) == 16
    assert len(first_test) == 4


def test_held_out_examples_are_padded_context_targets():
    examples = held_out_examples([["add", "salt"]], n=2)
    assert examples == [
        (("<s>",), "add"),
        (("add",), "salt"),
        (("salt",), "</s>"),
    ]


def test_evaluation_returns_all_models_and_finite_metrics():
    report = evaluate_all(
        [["add", "salt"], ["add", "pepper"], ["mix", "flour"], ["bake", "cake"]],
        seed=42,
        train_ratio=0.75,
        alpha=1.0,
    )

    assert report["dataset_instructions"] == 4
    assert report["train_instructions"] == 3
    assert report["test_instructions"] == 1
    assert [row["n"] for row in report["results"]] == [1, 2, 3]
    for row in report["results"]:
        assert 0 <= row["top1_accuracy"] <= 1
        assert row["top1_accuracy"] <= row["top5_accuracy"] <= 1
        assert row["perplexity"] > 0


def test_evaluation_writes_csv_and_json(tmp_path):
    report = evaluate_all(
        [["add", "salt"], ["add", "pepper"], ["mix", "flour"], ["bake", "cake"]],
        seed=7,
    )
    csv_path = tmp_path / "evaluation.csv"
    json_path = tmp_path / "evaluation.json"

    written_csv, written_json = write_evaluation(report, csv_path, json_path)

    assert written_csv.read_text(encoding="utf-8").startswith("model,n,")
    assert '"seed": 7' in written_json.read_text(encoding="utf-8")
