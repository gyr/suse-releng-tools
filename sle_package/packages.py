import re
from bs4 import BeautifulSoup
from rich.console import Console
from rich.table import Table
from subprocess import CalledProcessError

from sle_package.users import get_groups, get_users
from sle_package.utils.logger import logger_setup
from sle_package.utils.tools import (
    run_command,
    run_command_and_stream_output,
    running_spinner_decorator,
)


log = logger_setup(__name__)


@running_spinner_decorator
def is_shipped(api_url: str, package: str, productcomposer: str) -> bool:
    command = [
        "/bin/bash",
        "-c",
        f"osc -A {api_url} cat {productcomposer}",
    ]
    pattern = r"\b" + re.escape(package) + r"\b"
    for line in run_command_and_stream_output(command):
        if re.search(pattern, line):
            log.debug(line)
            return True
    return False


@running_spinner_decorator
def get_source_package(api_url: str, project: str, package: str) -> str:
    """
    Get the source package from OBS.

    :param api_url: OBS instance
    :param project: OBS project
    :param package: binary name
    :return: source package
    """
    command = f"osc -A {api_url} bse {package}"
    output = run_command(command.split())
    filtered_output = [
        line for line in output.stdout.splitlines() if line.startswith(f"{project} ")
    ]
    if len(filtered_output) == 0:
        raise RuntimeError(f"No source package found for {package} in {project}.")
    packages = []
    for line in filtered_output:
        items = line.split()
        item = items[1].split(":")
        if len(item) > 0:
            packages.append(item[0])
    source_package = set(packages)
    if len(source_package) != 1:
        log.debug(
            "More than 1 source package found for %s in %s: %s",
            package,
            project,
            source_package,
        )
    return str(next(iter(source_package)))


@running_spinner_decorator
def get_bugowner(api_url: str, package: str) -> tuple[list, bool]:
    """
    Given a source package return the OBS user of the bugowner"

    :param api_url: OBS instance
    :param project: OBS project
    :param package: binary name
    :return: source package
    """
    command = f"osc -A {api_url} api /search/owner?package={package}&filter=bugowner"
    bugowners = []
    is_group = False
    try:
        output = run_command(command.split())
        soup = BeautifulSoup(output.stdout, "lxml")
        people = soup.find_all("person")
        if len(people) != 0:
            bugowners = [person.get("name") for person in people]
            return bugowners, is_group

        groups = soup.find_all("group")
        if len(groups) != 0:
            is_group = True
            bugowners = [group.get("name") for group in groups]
            return bugowners, is_group

        log.debug("No bugowner found for %s.", package)
        return bugowners, is_group
    except CalledProcessError as e:
        raise RuntimeError(f"{package} has no bugowner") from e


def get_bugowner_info(api_url: str, user: str, is_group: bool) -> dict:
    """
    Given a source package return the OBS user of the bugowner"

    :param api_url: OBS instance
    :param project: OBS project
    :param package: binary name
    :return: source package
    """
    try:
        if is_group:
            return get_groups(api_url, user)
        return next(get_users(api_url, user))
    except CalledProcessError as e:
        raise RuntimeError(f"{user} not found.") from e


def build_parser(parent_parser, config) -> None:
    """
    Builds the parser for this script. This is executed by the main CLI
    dynamically.

    :param config: Lua config table
    :return: The subparsers object from argparse.
    """
    subparser = parent_parser.add_parser(
        "packages",
        help="Return OBS information for the given binary package.",
    )
    subparser.add_argument(
        "--project",
        "-p",
        dest="project",
        help=f"OBS/IBS project (DEFAULT = {config.common.default_project}).",
        type=str,
        default=f"{config.common.default_project}",
    )
    subparser.add_argument(
        "--product",
        "-P",
        dest="product",
        help=f"OBS/IBS product (DEFAULT = {config.common.default_product}).",
        type=str,
        default=f"{config.common.default_product}",
    )
    subparser.add_argument("binary_name", nargs="+", type=str, help="Binary name.")
    subparser.set_defaults(func=main)


def main(args, config) -> None:
    """
    Main method that get the OBS user from the bugowner for the given binary package.

    :param args: Argparse Namespace that has all the arguments
    :param config: Lua config table
    """
    console = Console()
    for binary in args.binary_name:
        try:
            table = Table(title=binary, show_header=False)
            if args.project == config.common.default_project:
                build_project = config.packages.get_build_project(config)
            else:
                build_project = f"{args.project}:Build"
            source_package = get_source_package(
                args.osc_instance, build_project, binary
            )
            table.add_row("Source package", source_package)
            if is_shipped(
                args.osc_instance,
                binary,
                config.packages.get_productcomposer(config),
            ):
                table.add_row("Shipped", f"YES - {args.product}")
            else:
                table.add_row("Shipped", "*** NO ***")
            bugowners, is_group = get_bugowner(args.osc_instance, source_package)
            for bugowner in bugowners:
                for key, value in get_bugowner_info(
                    args.osc_instance, bugowner, is_group
                ).items():
                    log.debug("%s: %s", key, value)
                    table.add_row(key, str(value))
            console.print(table)
        except RuntimeError as e:
            log.error(e)
