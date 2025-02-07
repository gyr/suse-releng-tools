#!/usr/bin/env python3
import argparse
import importlib
import sys
import urllib.error

import argcomplete  # type: ignore

from sle_package.utils.logger import logger_setup

PARSER = argparse.ArgumentParser(
    description="Return the list of artifacts from a OBS project"
)
PARSER.add_argument(
    "--osc-config",
    dest="osc_config",
    help="The location of the oscrc if a specific one should be used.",
)
PARSER.add_argument(
    "--osc-instance",
    dest="osc_instance",
    help="The URL of the API from the Open Buildservice instance that should be used.",
    default="https://api.suse.de",
)
SUBPARSERS = PARSER.add_subparsers(
    help="Help for the subprograms that this tool offers."
)

log = logger_setup(__name__)


def import_sle_module(name: str):
    """
    Imports a module

    :param name: Module in the sle_package package.
    """
    module = importlib.import_module(f".{name}", package="sle_package")
    module.build_parser(SUBPARSERS)


def main() -> None:
    module_list = ["artifacts", "requests"]
    for module in module_list:
        import_sle_module(module)
    argcomplete.autocomplete(PARSER)
    args = PARSER.parse_args()
    if "func" in vars(args):
        # Run a subprogramm only if the parser detected it correctly.
        try:
            args.func(args)
        except urllib.error.URLError as url_error:
            if "name or service not known" in str(url_error).lower():
                log.error(
                    "No connection to one of the tools. Please make sure the connection to the tools is available"
                    " before executing the program!"
                )
                sys.exit(1)
        return
    PARSER.print_help()
    sys.exit(1)


if __name__ == "__main__":
    main()
