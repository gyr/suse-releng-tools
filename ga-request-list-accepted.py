#!/usr/bin/env python3
import argparse
import logging
import list_accepted_pkgs

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='List accepted packages')
    parser.add_argument('-p', '--project', type=str, help='Project', required=True)
    parser.add_argument('-t', '--time', type=float, help='Only list requests changed in the last DAYS', required=True)
    parser.add_argument('-d', '--debug', action='store_true', help='debug output')

    args = parser.parse_args()

    level = logging.INFO
    if args.debug:
        level = logging.DEBUG
    logging.basicConfig(level=level)
    logger = logging.getLogger(__name__)

    # Prepare osc -> Config is ini style and needs to be converted first
    list_accepted_pkgs.osc_prepare(osc_config="/home/gyr/.config/osc/oscrc", osc_server="https://api.suse.de/")

    submit_requests, delete_requests = list_accepted_pkgs.main(
        "https://api.suse.de/", args.project, args.time
    )
    # Print both retrieved lists with format: "pkg-name (YYYY-MM-DDThh:mm:ss) hyperlink-to-request"
    print("==============================")
    print("SUBMIT REQUESTS")
    print("==============================")
    for request in submit_requests:
        print(
            f"({request.state.when}) {request.actions[0].src_package} https://build.suse.de/request/show/{request.reqid}"
        )
    print("==============================")
    print("DELETE REQUESTS")
    print("==============================")
    for request in delete_requests:
        print(
            f"({request.state.when}) {request.actions[0].tgt_package} https://build.suse.de/request/show/{request.reqid}"
        )
