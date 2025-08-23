"""Entry point for running the poker game."""

import argparse

from poker.game import main as game_main


def parse_args() -> argparse.Namespace:
    """Parse command line arguments for the game."""
    parser = argparse.ArgumentParser(description="Run the poker game")
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Show debug logging in the console",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    game_main(debug=args.debug)


if __name__ == "__main__":
    main()
