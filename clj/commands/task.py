"""Functions relatives to the `task` subcommand"""

import copy

from enum import Enum, unique
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


def load_tasks(task_file: Path) -> list():
    """Extract the tasks from a file path"""
    if not task_file.exists():
        return []

    with task_file.open("r", encoding="utf-8") as file_:
        return [
            {"status": Status(line.strip()[0]), "task": line.strip()[1:]} for line in file_
        ]


def store_tasks(task_file: Path, tasks) -> None:
    """Save the current tasks in a file"""
    with task_file.open("w", encoding="utf-8") as file_:
        file_.write("\n".join(["".join([str(v) for v in task.values()]) for task in tasks]))


def postpone_pending(previous_task_file: Path, current_task_file: Path) -> None:
    """Mark the PENDING tasks in the previous file as POSTPONED and append them to the set of
    current tasks as PENDING

    """
    postponed_tasks = []

    tasks = load_tasks(previous_task_file)
    for task in tasks:
        if task["status"] is Status.PENDING:
            task["status"] = Status.POSTPONED

        if task["status"] is Status.POSTPONED:
            new_task = copy.deepcopy(task)
            new_task["status"] = Status.PENDING
            postponed_tasks.append(new_task)

    store_tasks(previous_task_file, tasks)

    tasks = load_tasks(current_task_file) + postponed_tasks
    store_tasks(current_task_file, tasks)


def get_task_file(page_path: Path, *, create=False) -> Path:
    """Return the task file of the current page folder

    If `create` is `True` and the file does not exists, it will be created

    """
    task_file = page_path / "tasks.txt"

    if not task_file.exists():
        if not create:
            return None
        task_file.touch()

    return task_file


BOLD = "\033[1m"
END = "\033[0m"


@click.command(name="task")
@click.option("--all/--no-all", "all_", default=False)
@click.option("-a", "--add", type=str, multiple=True)
@click.option("-x", "--cross", type=int, multiple=True)
@click.option("-r", "--restore", type=int, multiple=True)
@click.option("-v", "--check", type=int, multiple=True)
@click.pass_obj
def cli(obj, all_, add, cross, check, restore): # pylint: disable=too-many-arguments
    """Task subcommand for clj group"""
    journal_page_path = obj["page"]

    task_file = get_task_file(journal_page_path, create=True)

    tasks = load_tasks(task_file)

    with task_file.open("r", encoding="utf-8") as file_:
        tasks = [{"status": Status(line[0]), "task": line.strip()[1:]} for line in file_]

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

    store_tasks(task_file, tasks)

    tasks = [t for t in tasks if all_ or t["status"] is Status.PENDING]

    for idx, task in enumerate(tasks):
        task = copy.deepcopy(task)
        print(f"{idx} {BOLD}{str(task['status'])}{END} {task['task']}")
