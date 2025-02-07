import datetime
import subprocess

from typing import List

from sle_package.utils.logger import logger_setup


log = logger_setup(__name__)


def run_command(command: List[str],
                capture_output=True,
                text=True,
                check=True):
    """
    Run shell command that does not require redirection.

    :param command: command to be executed in format of a list of strings
    :return: dict with stdout and sterr
    """
    try:
        result = subprocess.run(
            command, capture_output=capture_output, text=text, check=check
        )
        return result
    except subprocess.CalledProcessError as e:
        log.error("Failed to execute: %s", e)
        # if capture_output is True
        log.error("Stdout: %s", e.stdout)
        log.error("Stderr: %s", e.stderr)
        raise


def popen_command(command: List[str], text=True):
    """
    Used to run shell command that requires redirection, requires to run
    /bin/bash -c <shell_command>, e.g.:
        command = [
            "/bin/bash",
            "-c",
            f\"\"\"
            ex <(ls -l) << EOF
            g/^d/d
            %!sort
            %p
            q!
            EOF
            "\"\"
    :param command: command to be executed in format of a list of strings
    :return: string with stdout
    """
    try:
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=text,
        )

        stdout, stderr = process.communicate()

        if process.returncode != 0:
            log.error("Failed to execute: %s", command)
            log.error("Return code: %s", process.returncode)
            log.error("Stderr: %s", stderr)

        return stdout
    except FileNotFoundError:
        log.error("Command not found: %s", command[0])
        raise
    except OSError as e:
        log.error("Error executing command: %s", e)
        raise
    except Exception as e:
        log.error("Unexpected error: %s", e)
        raise


def run_command_and_stream_output(command):
    """
    Runs an external command and yields its output line by line.
    """
    try:
        with subprocess.Popen(command,
                              stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE,
                              text=True) as process:
            for line in iter(process.stdout.readline, ''):
                line = line.strip()
                if line:
                    yield line
            stderr = ""
            for line in iter(process.stderr.readline, ''):
                stderr.join(line)
            if process.returncode != 0:
                log.debug("Failed to execute: %s", command)
                log.debug("Return code: %s", process.returncode)
                log.debug("Stderr: %s", stderr)

            return process.returncode, stderr
    except FileNotFoundError:
        log.error("%s not found", command[0])
        raise
    except OSError as e:
        log.error("Error executing command: %s", e)
        raise
    except Exception as e:
        log.error("Unexpected error: %s", e)
        raise


def split_lines_ignore_empty(text: str) -> List[str]:
    """
    Splits a multi-line string into a list of lines, ignoring empty lines.
    :param text: multi-line string
    :return: string list
    """
    return [line.strip() for line in text.splitlines() if line.strip()]


def count_days(initial_date, final_date):
    """
    Calculates the number of days between 2 dates

    :param initial_date: initial date for the days calculation
    :param final_date: final date for the days calculation
    :return: number of the days between 2 dates
    """
    try:
        if isinstance(initial_date, str):
            start_date = datetime.datetime.strptime(initial_date, "%Y-%m-%d").date()
        else:
            start_date = initial_date
        if isinstance(final_date, str):
            end_date = datetime.datetime.strptime(final_date, "%Y-%m-%d").date()
        else:
            end_date = final_date
    except ValueError:
        log.error("Invalid date format (YYYY-MM-D)")
        raise

    delta = end_date - start_date
    return delta.days
