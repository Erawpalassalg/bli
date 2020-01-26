"""Main file for the clj commands group"""
import copy
import re
import shutil

from enum import Enum, unique
from datetime import datetime
from pathlib import Path
from typing import Union, Text

import click


@unique
class Status(Enum):
    """Task possible status"""

    PENDING = "•"
    DONE = "v"
    POSTPONED = ">"
    ERASED = "x"

    def __repr__(self):
        return self.value

    def __str__(self):
        return self.__repr__()


def _load_tasks(page_path: Path) -> list():
    """Extract the tasks from a file path"""
    if not page_path.exists():
        return []

    with page_path.open("r", encoding="utf-8") as file_:
        return [
            {"status": Status(line.strip()[0]), "task": line.strip()[1:]}
            for line in file_
        ]


def _store_tasks(page_path: Path, tasks) -> None:
    """Save the current tasks in a file"""
    with page_path.open("w", encoding="utf-8") as file_:
        file_.write(
            "\n".join(["".join([str(v) for v in task.values()]) for task in tasks])
        )


def _match(expression: Union[Text, re.Pattern], string: str) -> bool:
    """Check if a string is matched by a regex pattern or is in another string.
    Both checks are case-insensitive.

    """
    if isinstance(expression, re.Pattern):
        return expression.search(string) is not None
    return expression.lower() in string.lower()


def _init_journal() -> Path:
    """Initialize the journal by:
        - getting the page related to the system's current date
        - postponing all non-finished previous tasks (adding them to the current page
        - archiving the older page (if found))
    """

    def _postpone_pending_tasks(
        previous_page_path: Path,
        current_page_path: Path,  # pylint: disable=bad-continuation
    ) -> None:
        """Mark the PENDING tasks in the previous file as POSTPONED and append them to the set of
        current tasks as PENDING

        """
        postponed_tasks = []

        tasks = _load_tasks(previous_page_path)
        for task in tasks:
            if task["status"] is Status.PENDING:
                task["status"] = Status.POSTPONED

            if task["status"] is Status.POSTPONED:
                new_task = copy.deepcopy(task)
                new_task["status"] = Status.PENDING
                postponed_tasks.append(new_task)

        _store_tasks(previous_page_path, tasks)

        tasks = _load_tasks(current_page_path) + postponed_tasks
        _store_tasks(current_page_path, tasks)

    journal_path = Path.home() / ".clj"

    archive_path = journal_path / "archives"
    archive_path.mkdir(exist_ok=True, parents=True)

    current_page_path = journal_path / f"{datetime.date(datetime.now())}.txt"

    pages = list(journal_path.glob("*.txt"))

    if pages:
        if len(pages) > 1:
            raise RuntimeError("Journal directory is corrupted")

        if pages[0] != current_page_path:
            _postpone_pending_tasks(pages[0], current_page_path)
            shutil.move(str(pages[0]), str(archive_path))

    return current_page_path


def _update_status(tasks: dict, indexes: list, status: Status) -> None:
    """Update several tasks and set thei new status"""
    for idx in indexes:
        try:
            tasks[idx]["status"] = status
        except IndexError:
            click.echo(f"Task n° {idx} does not exist")


BOLD = "\033[1m"
END = "\033[0m"


@click.command()
@click.option("--all/--no-all", "all_", default=False)
@click.option("-f", "--filter", "filter_", type=click.UNPROCESSED, multiple=True)
@click.option("-a", "--add", type=str, multiple=True)
@click.option("-x", "--cross", type=int, multiple=True)
@click.option("-r", "--restore", type=int, multiple=True)
@click.option("-v", "--check", type=int, multiple=True)
@click.option("-pp", "->", "--postpone", type=int, multiple=True)
def cli(
    all_,
    filter_,
    add,
    cross,
    check,
    restore,
    postpone,
):  # pylint: disable=too-many-arguments
    """Bullet LIst, a simple, journalised todo list CLI tool"""
    current_page_path = _init_journal()

    # Build new task set
    tasks = _load_tasks(current_page_path)

    _update_status(tasks, restore, Status.PENDING)
    _update_status(tasks, cross, Status.ERASED)
    _update_status(tasks, check, Status.DONE)
    _update_status(tasks, postpone, Status.POSTPONED)

    for task in add:
        tasks.append({"status": Status.PENDING, "task": task})

    _store_tasks(current_page_path, tasks)

    # Display task set
    filter_ = [
        re.compile(exp[1:-1], re.I | re.M)
        if exp.startswith("/") and exp.endswith("/")
        else exp
        for exp in filter_
    ]

    for idx, task in enumerate(tasks):
        if all_ or task["status"] is Status.PENDING:
            result = (
                task
                if not filter_
                else next(
                    (task for filtr in filter_ if _match(filtr, task["task"])), False
                )
            )
            if result:
                click.echo(f"{idx} {BOLD}{str(task['status'])}{END} {task['task']}")


def main():
    """Entry point for poetry build"""
    cli()  # pylint: disable=no-value-for-parameter


if __name__ == "__main__":
    main()
