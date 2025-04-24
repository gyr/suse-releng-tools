import re

from sle_package.utils.logger import logger_setup
from sle_package.utils.tools import run_command, run_command_and_stream_output


log = logger_setup(__name__)


def list_packages(api_url: str, project: str) -> list[str]:
    """
    List all source packages from a OBS project

    :param api_url: OBS instance
    :param project: OBS project
    :return: list of source packages
    """
    command = f"osc -A {api_url} ls {project}"
    output = run_command(command.split())
    return output.stdout


def list_artifacs(api_url: str,
                  project: str,
                  repository: str,
                  pattern: str,
                  packages: list[str]) -> None:
    """
    List all artifacts filtered by pattern in the specified repoistory
    from a OBS project

    :param api_url: OBS instance
    :param project: OBS project
    :param repository: OBS repository
    :param pattern: used to filter the artifacts that will be returned
    :param project: list of source packages
    """
    log.debug(">> pattern = %s", pattern)
    pattern = re.compile(pattern)
    log.debug(">> pattern = %s", pattern)
    for package in packages:
        if re.search(pattern, package):
            command = [
                "/bin/bash",
                "-c",
                f"""
ex <(osc -A {api_url} ls {project} {package} -b -r {repository}) << EOF
# delete all lines that do not start with space
g/^[^ ]/d
# delete all lines that start with space + underscore
g/^[ ]*_/d
# delete no image files
g/sha256$\|report$\|json$\|milestone$\|packages$\|verified$\|asc$\|rpm$/d
# sort artifacts
%!sort
# print artifacts
%p
# exit ex
q!
EOF
exit 0
"""
            ]
            for line in run_command_and_stream_output(command):
                print(line)


def build_parser(parent_parser, config) -> None:
    """
    Builds the parser for this script. This is executed by the main CLI
    dynamically.

    :param config: Lua config table
    :return: The subparsers object from argparse.
    """
    subparser = parent_parser.add_parser("artifacts",
                                         help="Return the list of artifacts from a OBS project.")
    subparser.add_argument("--project",
                           "-p",
                           dest="project",
                           help=f'OBS/IBS project (DEFAULT = {config.artifacts.default_product}).',
                           type=str,
                           default=config.artifacts.default_product)
    subparser.set_defaults(func=main)


def main(args, config) -> None:
    """
    Main method that get the list of all artifacts from a given OBS project

    :param args: Argparse Namespace that has all the arguments
    :param config: Lua config table
    """
    # Parse arguments
    parameters = {
        "api_url": args.osc_instance,
        "project": args.project
    }
    packages = list_packages(**parameters).split()

    parameters.update({
        "repository": "images",
        "pattern": config.artifacts.images_pattern,
        "packages": packages
    })
    list_artifacs(**parameters)

    parameters.update({
        "repository": "product",
        "pattern": config.artifacts.prodcuts_pattern,
    })
    list_artifacs(**parameters)
