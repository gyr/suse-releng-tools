#!/usr/bin/env python3
import argparse
import logging
import shlex
import subprocess
import sys
import textwrap
import yaml


def convert_txt_to_dict(file_content):
    ret = dict()
    for line in file_content.splitlines():
        pkg, group = line.strip().split(':')
        ret.setdefault(pkg, [])
        ret[pkg].append(group)
    return ret

def convert_yml_to_dict(file_content, unsorted=False):
    ret = dict()
    try:
        parsed_yaml = yaml.safe_load(file_content)
        for module, packages in parsed_yaml.items():
            for package in packages:
                if unsorted:
                    ret[package] = ['unsorted']
                else:
                    ret[package] = [module]
    except yaml.YAMLError as e:
        logger.error(e, exc_info=True)
    return ret

def download_file(cmd):
    logger.debug(f'Executing: {cmd}')
    cmd_args = shlex.split(cmd)
    output = subprocess.run(cmd_args, capture_output=True, text=True)
    if output.returncode != 0:
        logger.warning(f'Failed to execute: {cmd}')
        logger.warning(output.stderr)
    return output

def get_yml_files(command, revision):
    ret = dict()
    yaml_files = [f'reference-summary.yml', f'reference-unsorted.yml', f'unneeded.yml']
    for file in yaml_files:
        cmd = command + f' {file}'
        if revision:
            cmd += f' -r {revision}'
        output = download_file(cmd)
        if output.returncode != 0:
            sys.exit(1)
        unsorted_flag = (file != yaml_files[0])
        content = convert_yml_to_dict(output.stdout, unsorted_flag)
        ret = {**ret, **content}
    return ret

def get_txt_file(cmd, revision):
    ret = dict()
    file = f'summary-staging.txt'
    cmd += f' {file}'
    if revision:
        cmd += f' -r {revision}'
    output = download_file(cmd)
    if output.returncode != 0:
        return None
    ret = convert_txt_to_dict(output.stdout)
    return ret

def get_file_content(project, revision):
    ret = dict()
    apiurl = f'https://api.suse.de/'
    package = f'000package-groups'
    cmd = f'osc -A {apiurl} cat {project} {package}'
    ret = get_txt_file(cmd, revision)
    if not ret:
        logger.debug(f'Failed to get summary-staging.txt, trying yaml files')
        ret = get_yml_files(cmd, revision)
    return ret

def write_summary_file(file, content):
    logger.debug(f'Summary report saved in {file}')
    with open(file, 'w') as f:
        f.write(content)

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
    parser = argparse.ArgumentParser(description='Report of package movements between 2 projects')
    parser.add_argument('-f', '--from-project', type=str, help='Origin project', required=True)
    parser.add_argument('-t', '--to-project', type=str, help='Target project', required=True)
    parser.add_argument('--from-revision-number', type=str, help='Origin revision number')
    parser.add_argument('--to-revision-number', type=str, help='Target revision number')
    parser.add_argument('-d', '--debug', action='store_true', help='debug output')


    args = parser.parse_args()

    level = logging.INFO
    if (args.debug):
        level = logging.DEBUG
    logging.basicConfig(level=level)
    logger = logging.getLogger(__name__)

    from_summary = get_file_content(args.from_project, args.from_revision_number)
    to_summary = get_file_content(args.to_project, args.to_revision_number)
    if (args.debug):
        write_summary_dict(args.from_project, from_summary)
        write_summary_dict(args.to_project, to_summary)

    report = calculcate_package_diff(from_summary, to_summary)
    if report:
        logger.info(f"\n{report}")
        if (args.debug):
            write_summary_file(f'summary-report.txt', report)
    else:
        logger.info(f'No package movement reported')
