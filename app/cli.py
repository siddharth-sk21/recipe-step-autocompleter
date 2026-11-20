"""Command-line entry point: `python -m app.cli --help`."""
import argparse

from .core import milestone_2, milestone_3


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(prog="recipe-step-autocompleter", description="Home cooks use this CLI tool to autocomplete incomplete recipe instructions, ensuring they don't miss steps and can follow recipes smoothly.")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("hello", help="check that everything is wired up")

    suggest = sub.add_parser("suggest", help="show likely next words")
    suggest.add_argument("prompt", nargs="+", help="partial recipe step")
    suggest.add_argument("-n", "--count", type=int, default=5, help="number of suggestions")

    generate = sub.add_parser("generate", help="generate a complete recipe-step continuation")
    generate.add_argument("prompt", nargs="+", help="partial recipe step")
    generate.add_argument("-n", "--count", type=int, default=10, help="maximum words to generate")
    generate.add_argument("--sample", action="store_true", help="sample instead of choosing the highest-probability word")
    generate.add_argument("--seed", type=int, help="random seed for repeatable sampling")

    args = parser.parse_args(argv)
    if args.command == "hello":
        print("Recipe Step Autocompleter is ready. Open README.md for your milestones.")
    elif args.command == "suggest":
        if args.count < 1:
            suggest.error("--count must be at least 1")
        model = milestone_2()
        prompt = " ".join(args.prompt)
        predictions = model.predict_next(prompt, limit=args.count)
        if not predictions:
            print("No suggestions available.")
        for word, probability in predictions:
            print(f"{word}\t{probability:.4f}")
    elif args.command == "generate":
        if args.count < 1:
            generate.error("--count must be at least 1")
        prompt = " ".join(args.prompt)
        print(milestone_3(
            prompt,
            max_words=args.count,
            sample=args.sample,
            seed=args.seed,
        ))


if __name__ == "__main__":
    main()
