"""Main file for the clj commands group"""
import copy
import shutil

from enum import Enum, unique
from datetime import datetime
from pathlib import Path

import click

@unique
class Status(Enum):
    """Task possible status"""

    PENDING = "•"
    DONE = "v"
    POSTPONED = ">"
    ERASED = "x"

    def int_val(self):
        """Int value for sorting purposes"""
        return {"•": 1, ">": 2, "v": 3, "x": 4}[self.value]

    def __repr__(self):
        return self.value

    def __str__(self):
        return self.__repr__()


def load_tasks(page_path: Path) -> list():
    """Extract the tasks from a file path"""
    if not page_path.exists():
        return []

    with page_path.open("r", encoding="utf-8") as file_:
        return [
            {"status": Status(line.strip()[0]), "task": line.strip()[1:]} for line in file_
        ]


def store_tasks(page_path: Path, tasks) -> None:
    """Save the current tasks in a file"""
    with page_path.open("w", encoding="utf-8") as file_:
        file_.write("\n".join(["".join([str(v) for v in task.values()]) for task in tasks]))


def postpone_pending(previous_page_path: Path, current_page_path: Path) -> None:
    """Mark the PENDING tasks in the previous file as POSTPONED and append them to the set of
    current tasks as PENDING

    """
    postponed_tasks = []

    tasks = load_tasks(previous_page_path)
    for task in tasks:
        if task["status"] is Status.PENDING:
            task["status"] = Status.POSTPONED

        if task["status"] is Status.POSTPONED:
            new_task = copy.deepcopy(task)
            new_task["status"] = Status.PENDING
            postponed_tasks.append(new_task)

    store_tasks(previous_page_path, tasks)

    tasks = load_tasks(current_page_path) + postponed_tasks
    store_tasks(current_page_path, tasks)


BOLD = "\033[1m"
END = "\033[0m"


@click.command()
@click.option("--all/--no-all", "all_", default=False)
@click.option("-a", "--add", type=str, multiple=True)
@click.option("-x", "--cross", type=int, multiple=True)
@click.option("-r", "--restore", type=int, multiple=True)
@click.option("-v", "--check", type=int, multiple=True)
def cli(all_, add, cross, check, restore): # pylint: disable=too-many-arguments
    """Task subcommand for clj group"""
    journal_path = Path.home() / ".clj" / "default"

    archive_path = journal_path / "archives"
    archive_path.mkdir(exist_ok=True, parents=True)

    current_page_path = journal_path / f"{datetime.date(datetime.now())}.txt"

    pages = list(journal_path.glob("*.txt"))

    if pages:
        if len(pages) > 1:
            raise RuntimeError("Journal directory is corrupted")

        if pages[0] != current_page_path:
            postpone_pending(pages[0], current_page_path)
            shutil.move(str(pages[0]), str(archive_path))

    tasks = load_tasks(current_page_path)

    for idx in restore:
        try:
            tasks[idx]["status"] = Status.PENDING
        except IndexError:
            print(f"Task n° {idx} does not exist")

    for idx in cross:
        try:
            tasks[idx]["status"] = Status.ERASED
        except IndexError:
            print(f"Task n° {idx} does not exist")

    for idx in check:
        try:
            tasks[idx]["status"] = Status.DONE
        except IndexError:
            print(f"Task n° {idx} does not exist")

    for task in add:
        tasks.append({"status": Status.PENDING, "task": task})

    tasks = sorted(tasks, key=lambda task: task["status"].int_val())

    store_tasks(current_page_path, tasks)

    tasks = [t for t in tasks if all_ or t["status"] is Status.PENDING]

    for idx, task in enumerate(tasks):
        task = copy.deepcopy(task)
        print(f"{idx} {BOLD}{str(task['status'])}{END} {task['task']}")


def main():
    """Entry point for poetry build"""
    cli()  # pylint: disable=no-value-for-parameter


if __name__ == "__main__":
    main()
