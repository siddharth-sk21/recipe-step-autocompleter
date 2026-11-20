"""Command-line entry point: `python -m app.cli --help`."""
import argparse


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(prog="recipe-step-autocompleter", description="Home cooks use this CLI tool to autocomplete incomplete recipe instructions, ensuring they don't miss steps and can follow recipes smoothly.")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("hello", help="check that everything is wired up")
    # TODO: add your own commands here as you work through the milestones.
    args = parser.parse_args(argv)
    if args.command == "hello":
        print("Recipe Step Autocompleter is ready. Open README.md for your milestones.")


if __name__ == "__main__":
    main()
