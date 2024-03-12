"""The main application runner."""
from pathlib import PurePath
from argparse import ArgumentParser, Namespace
from os.path import expanduser

from textual.app import App

from .. import __version__
from ..screens import Main
from ..chain import run_query, get_deeplake


class MainApp(App[None]):
    """The main application class."""

    def __init__(self, cli_args: Namespace) -> None:
        """Initialise the application."""
        super().__init__()
        self._args = cli_args

    def on_mount(self) -> None:
        """Set up the application after the DOM is ready."""
        self.push_screen(
            Main(" ".join(self._args.source) if self._args.source else expanduser("~"))
        )


def on_input_submitted() -> None:
    """Handle the user submitting the input."""
    args = get_args()
    dataset_source_path = " ".join(args.source) if args.source else expanduser("~")
    path = PurePath(dataset_source_path)
    db = get_deeplake(path.parent.name)
    results = run_query(db, "What is this source code about?", dataset_source_path)
    print(f"Results is: {results}")


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
        "--source",
        "-s",
        help="The path to the source of the dataset to be used",
        nargs="*",
    )
    return parser.parse_args()


def run() -> None:
    """Run the application."""
    on_input_submitted()
