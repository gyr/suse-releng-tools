import sys

from sle_package.utils.logger import logger_setup
from sle_package.utils.tools import run_command, run_command_and_stream_output, pager_command, ask_action


log = logger_setup(__name__, verbose=True)


def list_requests(api_url: str,
                  project: str) -> list[tuple[str, str, str]]:
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
ex <(osc -A {api_url} review list --type set_bugowner {project}) << EOF
# filter lines
v/^\([0-9]\| *set_bugowner:\|.* sle-release-managers\)/d
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
        # ['000000', 'State:review', 'By:foo', 'When:2025-03-20T18:20:31', 'set_bugowner:', 'java-maintainers', 'SUSE:SLFO:Main/picocli', 'Review', 'by', 'Group', 'is', 'new:', 'sle-release-managers']
        request = (line_fields[0], line_fields[6].rsplit('/', 1)[1].split('@', 1)[0], line_fields[5])
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
    groups: tuple[str, str] = ('sle-release-managers', 'sle-staging-managers')
    for group in groups:
        command = f"osc -A {api_url} review accept -m 'OK' -G {group} {request}"
        output = run_command(command.split())
        print(f'{group}: {output.stdout}')


def build_parser(parent_parser, config) -> None:
    """
    Builds the parser for this script. This is executed by the main CLI
    dynamically.

    :param config: Lua config table
    :return: The subparsers object from argparse.
    """
    subparser = parent_parser.add_parser("bugowners", help="Review bugowner requests.")
    subparser.add_argument("--project",
                           "-p",
                           dest="project",
                           help=f'OBS/IBS project (DEFAULT = {config.common.default_project}).',
                           type=str,
                           default=config.common.default_project)
    subparser.set_defaults(func=main)


def main(args, config) -> None:
    """
    Main method that get the list of all artifacts from a given OBS project

    :param args: Argparse Namespace that has all the arguments
    :param config: Lua config table
    """
    requests = list_requests(args.osc_instance, args.project)

    if len(requests) == 0:
        print(">>> No pending bugowner reviews.")
        sys.exit(0)

    print(f">>> Bugowner request(s) to be reviewed:")
    for request in requests:
        print(*request, sep=" - ")

    start_review = ask_action(f">>> Start the review?")
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
