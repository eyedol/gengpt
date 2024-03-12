import sys
from os.path import expanduser
from pathlib import Path, PurePath
from typing import Iterable

from textual.app import ComposeResult
from textual.containers import Container, VerticalScroll
from textual.reactive import var
from textual.screen import Screen
from textual.widgets import DirectoryTree, Footer, Header, Input, Markdown
import logging
from textual.logging import TextualHandler

from langchain.vectorstores import DeepLake

from ..chain import run_query, get_deeplake

logging.basicConfig(
    level="NOTSET", format="%(message)s", datefmt="[%X]", handlers=[TextualHandler()]
)

# log = logging.getLogger("rich")


class FilteredDirectoryTree(DirectoryTree):
    def filter_paths(self, paths: Iterable[Path]) -> Iterable[Path]:
        return [path for path in paths if not path.name.startswith(".")]


class Main(Screen):
    """The main screen for the application."""

    CSS_PATH = "css/app.css"

    BINDINGS = [
        ("f", "toggle_files", "Toggle Files"),
        ("q", "app.quit", "Quit"),
    ]

    dataset_source_path: str = expanduser("~") if len(sys.argv) < 2 else sys.argv[1]
    show_tree = var(True)

    def __init__(self, dataset_source_path: str | None = None) -> None:
        """Initialise the main screen."""

        super().__init__()
        self.dataset_source_path = dataset_source_path

    def watch_show_tree(self, show_tree: bool) -> None:
        """Called when show_tree is modified."""
        self.set_class(show_tree, "-show-tree")

    def compose(self) -> ComposeResult:
        yield Header()
        with Container():
            yield FilteredDirectoryTree(self.dataset_source_path, id="tree-view")
            with Container():
                with VerticalScroll(id="results-container"):
                    yield Markdown(id="results")
                yield Input(
                    placeholder="Enter a prompt to generate code or explain code"
                )
        yield Footer()

    def on_mount(self) -> None:
        """Called when app starts."""
        self.query_one(Markdown).focus()

    async def on_input_submitted(self, message: Input.Submitted) -> None:
        """Handle the user submitting the input."""
        if message.value:
            dataset_dir = self.dataset_source_path.replace(
                Path(self.dataset_source_path).name, ""
            )
            logging.info(f"datasource {dataset_dir}")
            path = PurePath(self.dataset_source_path)
            db = get_deeplake(path.parent.name)
            results = run_query(db, message.value, dataset_dir)
            self.query_one("#results", Markdown).update(results)
        else:
            # Clear the results
            self.query_one("#results", Markdown).update("")

    def on_directory_tree_file_selected(
        self, event: DirectoryTree.FileSelected
    ) -> None:
        """Called when the user click a file in the directory tree."""
        event.stop()
        self.dataset_source_path = str(event.path)

    def action_toggle_files(self) -> None:
        """Called in response to key binding."""
        self.show_tree = not self.show_tree
