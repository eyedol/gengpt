"""The main application runner."""
import platform
import tempfile

from pathlib import Path
from argparse import ArgumentParser, Namespace
from os.path import expanduser

from textual.app import App

from .. import __version__
from ..screens import Main


class MainApp(App[None]):
    """The main application class."""

    def __init__(self, cli_args: Namespace) -> None:
        """Initialise the application."""
        super().__init__()
        self._args = cli_args

    def on_mount(self) -> None:
        """Set up the application after the DOM is ready."""
        self.push_screen(
            Main(
                " ".join(self._args.source) if self._args.source else expanduser("~"),
                self._args.store,
            )
        )


def get_args() -> Namespace:
    """Parse and return the command line arguments."""

    parser = ArgumentParser(
        prog="gengpt",
        description="GenGPT -- A .",
        epilog=f"v{__version__}",
    )

    # Add --version
    parser.add_argument(
        "-v",
        "--version",
        help="Show version information.",
        action="version",
        version=f"%(prog)s {__version__}",
    )

    parser.add_argument(
        "source", help="The path to the source of the dataset to be trained", nargs="*"
    )
    parser.add_argument(
        "store",
        help="The path where to store the trained dataset",
        nargs="*",
        default=_get_temp_dir(),
    )
    return parser.parse_args()


def run() -> None:
    """Run the application."""
    MainApp(get_args()).run()


def _get_temp_dir():
    return tempfile.mkdtemp(prefix="gen_", suffix="_gpt")
