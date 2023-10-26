#!/usr/bin/env python3
import argparse
import logging
import shlex
import subprocess
import sys
import textwrap


def download_file(cmd):
    logger.debug(f'Executing: {cmd}')
    cmd_args = shlex.split(cmd)
    output = subprocess.run(cmd_args, capture_output=True, text=True)
    if output.returncode != 0:
        logger.error(f'Failed to execute: {cmd}')
        logger.error(output.stderr)
        sys.exit(1)
    return output

def convert_txt_to_dict(file_content):
    ret = dict()
    for line in file_content.splitlines():
        pkg, group = line.strip().split(':')
        ret.setdefault(pkg, [])
        ret[pkg].append(group)
    return ret

def write_summary_file(file, content):
    logger.debug(f'Summary report saved in {file}')
    with open(file, 'w') as f:
        f.write(content)

def get_file_content(project, package, debug):
    ret = dict()
    apiurl = f'https://api.suse.de/'
    cmd = f'osc -A {apiurl} cat {project} {package} summary-staging.txt'
    output = download_file(cmd)
    ret = convert_txt_to_dict(output.stdout)
    if debug:
        write_summary_dict(package, ret)
    return ret

def write_summary_dict(file, content):
    logger.debug(f'List of {file} packages saved in {file}')
    output = []
    for pkg in sorted(content):
        for group in sorted(content[pkg]):
            output.append(f"{pkg}:{group}")

    with open(file, 'w') as f:
        for line in sorted(output):
            f.write(line + '\n')

def calculcate_package_diff(old_file, new_file):

    # remove common part
    keys = list(old_file.keys())
    for key in keys:
        if new_file.get(key, []) == old_file[key]:
            del new_file[key]
            del old_file[key]

    if not old_file and not new_file:
        return None

    removed = dict()
    for pkg in old_file:
        old_groups = old_file[pkg]
        if new_file.get(pkg):
            continue
        removekey = ','.join(old_groups)
        removed.setdefault(removekey, [])
        removed[removekey].append(pkg)

    report = ''
    for rm in sorted(removed.keys()):
        report += f"* Remove from {rm}\n   "
        paragraph = ', '.join(removed[rm])
        report += "\n".join(textwrap.wrap(paragraph, width=90, break_long_words=False, break_on_hyphens=False))
        report += "\n"

    moved = dict()
    for pkg in old_file:
        old_groups = old_file[pkg]
        new_groups = new_file.get(pkg)
        if not new_groups:
            continue
        movekey = ','.join(old_groups) + ' to ' + ','.join(new_groups)
        moved.setdefault(movekey, [])
        moved[movekey].append(pkg)

    for move in sorted(moved.keys()):
        report += f"* Move from {move}\n   "
        paragraph = ', '.join(moved[move])
        report += "\n".join(textwrap.wrap(paragraph, width=90, break_long_words=False, break_on_hyphens=False))
        report += "\n"

    added = dict()
    for pkg in new_file:
        if pkg in old_file:
            continue
        addkey = ','.join(new_file[pkg])
        added.setdefault(addkey, [])
        added[addkey].append(pkg)

    for group in sorted(added):
        report += f"* Add to {group}\n   "
        paragraph = ', '.join(added[group])
        report += "\n".join(textwrap.wrap(paragraph, width=90, break_long_words=False, break_on_hyphens=False))
        report += "\n"

    return report.strip()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Report of package movements on Staging')
    parser.add_argument('-p', '--project', type=str, help='Staging project', required=True)
    parser.add_argument('-d', '--debug', action='store_true', help='debug output')


    args = parser.parse_args()

    level = logging.INFO
    if (args.debug):
        level = logging.DEBUG
    logging.basicConfig(level=level)
    logger = logging.getLogger(__name__)

    packages = {
        f'000product': None,
        f'000package-groups': None,
    }
    for package in packages.keys():
        packages[package] = get_file_content(args.project, package, args.debug)

    #report = calculcate_package_diff(packages[f'000product'], packages[f'000package-groups'])
    report = calculcate_package_diff(packages[f'000package-groups'], packages[f'000product'])
    if report:
        print(f"{report}")
        if (args.debug):
            write_summary_file(f'summary-report.txt', report)
    else:
        logger.info(f'No package movement reported')
