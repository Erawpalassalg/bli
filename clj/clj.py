"""Main file for the clj commands group"""
import shutil

from datetime import datetime
from pathlib import Path

import click

from .commands import task  # pylint: disable=relative-beyond-top-level


@click.group()
@click.pass_context
def cli(ctx):
    """clj main command groups"""
    journal_path = Path.home() / ".clj"

    archive_path = journal_path / "archives"
    archive_path.mkdir(exist_ok=True, parents=True)

    current_page_path = journal_path / str(datetime.date(datetime.now()))
    current_page_path.mkdir(exist_ok=True, parents=True)

    folders = list(journal_path.glob("*"))
    folders.remove(archive_path)
    folders.remove(current_page_path)

    if len(folders) > 1:
        raise RuntimeError("Journal directory is corrupted")

    if folders:
        folder = folders[0]

        # Postpone tasks
        previous_task_file = task.get_task_file(folder)
        current_task_file = task.get_task_file(current_page_path, create=True)

        task.postpone_pending(previous_task_file, current_task_file)

        # Archive previous journal page
        shutil.move(str(folder), str(archive_path))

    ctx.obj = {
        "journal": journal_path,
        "page": current_page_path,
        "archive": archive_path,
    }


def main():
    """Entry point for poetry build"""
    cli.add_command(task.cli)
    cli()  # pylint: disable=no-value-for-parameter


if __name__ == "__main__":
    main()
