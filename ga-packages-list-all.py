#!/usr/bin/env python3
import argparse
import logging
import shlex
import subprocess
import sys
import xml.etree.ElementTree as ET


def get_build_result(project):
    apiurl = f'https://api.suse.de/'
    cmd = f'osc -A {apiurl} api /build/{project}/_result'
    logger.debug(f'Executing: {cmd}')
    cmd_args = shlex.split(cmd)
    output = subprocess.run(cmd_args, capture_output=True, text=True)
    if output.returncode != 0:
        logger.error(f'Failed to execute: {cmd}')
        logger.error(output.stderr)
        sys.exit(1)
    return output.stdout

def mainElementTree(project):
    #tree = ET.parse("build-result.xml")
    tree = ET.ElementTree(ET.fromstring(get_build_result(project)))
    root = tree.getroot()
    #print(root.tag)
    #print(root.attrib)
    #print("====================")
    project_packages = {}
    for repository in root:
        if repository.attrib["repository"] != "ports":
            #print("====================")
            #print(repository.tag)
            #print(repository.attrib)
            #print(repository.text)
            #print(repository.attrib["repository"], repository.attrib["arch"])
            if repository.attrib["repository"] not in project_packages:
                project_packages[repository.attrib["repository"]] = []
            #print("====================")
            for package in repository:
                if package.attrib["code"] != "excluded" and \
                        package.attrib["code"] != "disabled" and \
                        package.attrib["code"] != "unknown":
                    #print(package.tag)
                    #print(package.attrib)
                    #print(package.text)
                    #print(package.attrib["package"])
                    if package.attrib["package"] not in project_packages[repository.attrib["repository"]]:
                        project_packages[repository.attrib["repository"]].append(package.attrib["package"])
                    #print("--------------------")
    for repository in project_packages.keys():
        print("%if \"%_repository\" == \"{}\"".format(repository))
        project_packages[repository].sort()
        for package in project_packages[repository]:
            print("BuildFlags: onlybuild:{}".format(package))
        print("%endif\n")



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Report of package movements on Staging')
    parser.add_argument('-p', '--project', type=str, help='Staging project', required=True)
    parser.add_argument('-d', '--debug', action='store_true', help='debug output')


    args = parser.parse_args()

    level = logging.INFO
    if (args.debug):
        level = logging.DEBUG
    logging.basicConfig(level=level)
    logger = logging.getLogger(__name__)
    #mainMinidom()
    mainElementTree(args.project)
