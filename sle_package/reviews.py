import argparse
import sys

from sle_package.utils.logger import logger_setup
from sle_package.utils.tools import run_command, run_command_and_stream_output, pager_command, ask_action


log = logger_setup(__name__, verbose=True)


def valid_staging(staging: str) -> str:
    """
    Validate if a string is a single letter.

    :param staging: string to check
    :return evaluated string
    """
    try:
        if len(staging) != 1 or not staging.isalpha():
            msg = "Staging must be a single letter"
            raise argparse.ArgumentTypeError(msg)
        return staging
    except ValueError as exc:
        msg = f"Not a valid staging: '{staging}'. Must a single letter."
        raise argparse.ArgumentTypeError(msg) from exc


def list_requests(api_url: str,
                  project: str,
                  staging: str) -> list[tuple[str, str]]:
    """
    List all source packages from a OBS project

    :param api_url: OBS instance
    :param project: OBS project
    :return: list of source packages
    """
    requests = []
    command = [
        "/bin/bash",
        "-c",
        f"""
ex <(osc -A {api_url} review list -P {staging} {project}) << EOF
# filter lines
v/^\([0-9]\| *submit:\| *delete:\|.* sle-release-managers\)/d
# :g/^/: The :global command. /^/ matches every line (beginning of line).
# if line('.') < line('$')-1: Checks if the current line is at least two lines away from the end of the file. This condition prevents attempting to join lines that don't exist.
# .,+2join: Joins the current line and the next two lines.
# endif: Closes the if statement.
g/^/if line('.') < line('$')-1 | .,+2join | endif
# delete reviewed requests
g/Review by Group      is accepted:  sle-release-managers(/d
# filter request id
##%s/\s.*//
%p
q!
EOF
[ $? -ne 0 ] && exit 0
"""
    ]
    for line in run_command_and_stream_output(command):
        line_fields = line.split()
        # ['000000', 'State:review(approved)', 'By:foo', 'When:2025-02-14T15:29:41', 'submit:', 'SUSE:SLFO:Main/utempter', '->', 'SUSE:SLFO:Main', 'Review', 'by', 'Group', 'is', 'new:', 'sle-release-managers']
        request = (
            line_fields[0],
            line_fields[5].rsplit('/', 1)[1].split('@', 1)[0].replace('.SUSE_SLFO_Main', '')
        )
        requests.append(request)
    return requests


def show_request(api_url: str, request: str) -> None:
    """
    Show reviewed request details

    :param api_url: OBS instance
    :param request: request ID
    """
    command = f"osc -A {api_url} review show -d {request}"
    output = run_command(command.split())
    pager_command(['delta'], output.stdout)


def approve_request(api_url: str, request: str) -> None:
    """
    Approve request

    :param api_url: OBS instance
    :param request: request ID
    """
    command = f"osc -A {api_url} review accept -m 'OK' -G sle-release-managers {request}"
    output = run_command(command.split())
    print(output.stdout)


def build_parser(parent_parser) -> None:
    """
    Builds the parser for this script. This is executed by the main CLI
    dynamically.

    :return: The subparsers object from argparse.
    """
    subparser = parent_parser.add_parser("reviews", help="Review submit and delete requests.")
    subparser.add_argument("--project",
                           "-p",
                           dest="project",
                           help="OBS/IBS project.",
                           type=str,
                           required=True)
    subparser.add_argument("--staging",
                           "-s",
                           dest="staging",
                           type=valid_staging,
                           help="Staging letter.",
                           required=True)
    subparser.set_defaults(func=main)


def main(args) -> None:
    """
    Main method that get the list of all artifacts from a given OBS project

    :param args: Argparse Namespace that has all the arguments
    """
    # Parse arguments
    if args.staging:
        staging = f"{args.project}:Staging:{args.staging}"

    requests = list_requests(args.osc_instance, args.project, staging)

    if len(requests) == 0:
        print(">>> No pending reviews.")
        sys.exit(0)

    print(f">>> Request(s) to be reviewed on {staging}:")
    for request in requests:
        print(*request, sep=" - ")

    start_review = ask_action(f">>> Start the review of {staging}?")
    if start_review == 'n':
        sys.exit(0)

    for request in requests:
        review_request = ask_action(f">>> Review {request[0]} - {request[1]}?",
                                    ['y', 'n', 'a'])
        if review_request == "y":
            show_request(args.osc_instance, request[0])
            request_approval = ask_action(f">>> Approve {request[0]} - {request[1]}?")
            if request_approval == "y":
                approve_request(args.osc_instance, request[0])
        elif review_request == "a":
            sys.exit(0)
    print(">>> All reviews done.")
