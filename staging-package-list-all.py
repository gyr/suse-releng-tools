#!/usr/bin/env python3
import argparse
import logging
import shlex
import subprocess
import sys
import xml.etree.ElementTree as ET


def run_osc(cmd):
    logger.debug(f'Executing: {cmd}')
    apiurl = f'https://api.suse.de/'
    cmd = f'osc -A {apiurl} {cmd}'
    cmd_args = shlex.split(cmd)
    output = subprocess.run(cmd_args, capture_output=True, text=True)
    if output.returncode != 0:
        logger.error(f'Failed to execute: {cmd}')
        logger.error(output.stderr)
        sys.exit(1)
    return output.stdout

def get_all_staging_packages(project):
    cmd = f'api /build/{project}/_result'
    return ET.ElementTree(ET.fromstring(run_osc(cmd)))

def get_staging_packages(project):
    cmd = f'ls {project}'
    packages = list(run_osc(cmd).split("\n"))
    packages = list(filter(None, packages))
    return packages

def mainElementTree(project):
    tree =  get_all_staging_packages(project)
    root = tree.getroot()
    staging_packages = get_staging_packages(project)
    project_packages = []
    for repository in root:
        for package in repository:
            for staging_package in staging_packages:
                if staging_package in package.attrib["package"] and \
                        package.attrib["package"] not in project_packages:
                    project_packages.append(package.attrib["package"])
    project_packages.sort()
    for package in project_packages:
        print("BuildFlags: onlybuild:{}".format(package))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='List Staging packages to be added in Devel:ReleaseManagement:StagingTest prjconf')
    parser.add_argument('-p', '--project', type=str, help='Staging project', required=True)
    parser.add_argument('-d', '--debug', action='store_true', help='debug output')

    args = parser.parse_args()

    level = logging.INFO
    if (args.debug):
        level = logging.DEBUG
    logging.basicConfig(level=level)
    logger = logging.getLogger(__name__)
    mainElementTree(args.project)
