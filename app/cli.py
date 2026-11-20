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

    complete = sub.add_parser("complete", help="interactively extend a partial recipe step")
    complete.add_argument("prompt", nargs="+", help="partial recipe step")
    complete.add_argument("-n", "--count", type=int, default=5, help="number of suggestions")
    complete.add_argument("-s", "--steps", type=int, default=3, help="number of completion rounds")
    complete.add_argument("--choose", type=int, help="choose a suggestion automatically")

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
    elif args.command == "complete":
        if args.count < 1:
            complete.error("--count must be at least 1")
        if args.steps < 1:
            complete.error("--steps must be at least 1")

        model = milestone_2()
        prompt = " ".join(args.prompt)
        for _ in range(args.steps):
            predictions = model.predict_next(prompt, limit=args.count)
            if not predictions:
                break

            print(f"Current step: {prompt}")
            for index, (word, probability) in enumerate(predictions, start=1):
                print(f"{index}. {word} ({probability:.4f})")

            if args.choose is not None:
                choice = args.choose
            else:
                try:
                    choice = int(input("Choose a word number: ").strip())
                except (EOFError, ValueError):
                    break

            if choice < 1 or choice > len(predictions):
                print("Invalid choice.")
                break
            prompt = f"{prompt} {predictions[choice - 1][0]}"

        print(f"Final step: {prompt}")


if __name__ == "__main__":
    main()
