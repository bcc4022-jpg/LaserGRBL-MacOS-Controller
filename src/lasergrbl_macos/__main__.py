from __future__ import annotations

import argparse

from .app import run
from .i18n import SUPPORTED_LANGUAGES


def main() -> int:
    parser = argparse.ArgumentParser(description="Control GRBL-compatible laser engravers from macOS.")
    parser.add_argument("--demo", action="store_true", help="Run with a simulated controller and no hardware.")
    parser.add_argument(
        "--lang",
        choices=SUPPORTED_LANGUAGES,
        help="Interface language. Defaults to LASERGRBL_LANG or the macOS language setting.",
    )
    arguments = parser.parse_args()
    return run(demo_mode=arguments.demo, language=arguments.lang)


if __name__ == "__main__":
    raise SystemExit(main())
