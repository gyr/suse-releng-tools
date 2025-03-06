import datetime
import subprocess
import sys
from typing import Any, Generator


from sle_package.utils.logger import logger_setup


log = logger_setup(__name__)


def run_command(command: list[str],
                capture_output=True,
                text=True,
                check=True) -> dict[Any, Any]:
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


def popen_command(command: list[str], text=True) -> str:
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


def run_command_and_stream_output(command: list[str]) -> Generator:
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
                    log.debug(">> %s", line)
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


def pager_command(command: list[str], output) -> None:
    """
    Pages the given output using command

    :param command: pager command, e.g ['less', '-F', '-R', '-S', '-X', '-K']
    :param output: output to be paged
    """
    try:
        # Use less as the pager
        pager = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=sys.stdout)
        try:
            if isinstance(output, str):  # Handle single string or list of strings
                pager.stdin.write(output.encode())
            elif isinstance(output, list):
                for line in output:
                    pager.stdin.write((line + '\n').encode())
            pager.stdin.close()
            pager.wait()
        except KeyboardInterrupt:  # Allow user to exit less with Ctrl+C
            pass
        except BrokenPipeError:  # Allow user to exit less with Ctrl+C
            pass
        finally:  # Ensure pager is terminated
            pager.terminate()
    except FileNotFoundError:  # Handle cases where less is not installed
        log.error("%s command not found. Printing output directly:", command[0])
        log.error("%s", output)


def split_lines_ignore_empty(text: str) -> list[str]:
    """
    Splits a multi-line string into a list of lines, ignoring empty lines.
    :param text: multi-line string
    :return: string list
    """
    return [line.strip() for line in text.splitlines() if line.strip()]


def count_days(initial_date, final_date) -> int:
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


def ask_action(prompt: str, allowed_responses=None) -> str:
    """
    Asks the user what action the user wants and handles the response.

    Args:
        prompt: The question to ask the user.
        allowed_responses: A set of allowed responses. Defaults to ["y", "n"].
    """
    if allowed_responses is None:
        allowed_responses = ['y', 'n']
    allowed_string = ", ".join(allowed_responses)
    prompt += f' ({allowed_string}): '

    while True:
        response = input(prompt).strip().lower()
        if response in allowed_responses:
            return response
        log.error("Invalid response. Please enter one of: %s", allowed_string)
