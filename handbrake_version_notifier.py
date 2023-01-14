""" checks for new versions of handbrake """

import os
import sys
from typing import Any, Dict, Tuple

import click
from loguru import logger
import requests
from semver import Version # type: ignore

URL = "https://api.github.com/repos/Handbrake/Handbrake/releases"

RUNNING_IN_AWS = bool(os.getenv('AWS_EXECUTION_ENV'))

def semver_key_sort(value: Dict[str, Any]) -> Version:
    """ sorting function """
    parsed = Version.parse(str(value.get('tag_name')))
    return parsed

def get_last_vals() -> Tuple[Version, str]:
    """ gets the last values """
    logger.debug(f"Running in AWS? {RUNNING_IN_AWS}")
    if os.getenv('LAST_SEEN'):
        last_seen = Version.parse(os.environ['LAST_SEEN'])
        last_source = "env"
    elif os.path.exists('lastseen.txt'):
        with open('lastseen.txt', encoding="utf-8") as file_handle:
            last_seen = Version.parse(file_handle.read().strip())
        last_source = "disk"
    else:
        logger.debug("No last_seen set, will need to write one")
        last_seen = Version.parse("0.0.0")
        last_source = "default"
    return last_seen, last_source

@click.command()
@click.option("--debug", "-d", is_flag=True, default=False)
def cli(debug: bool=False) -> None:
    """ cli interface """
    if not debug:
        logger.remove()
        logger.add(level="INFO", sink=sys.stdout)

    last_seen, last_source = get_last_vals()

    try:
        response = requests.get(url=URL, timeout=30)
        response.raise_for_status()
    except Exception as error_message: # pylint: disable=broad-except
        logger.error(f"Request failed: {error_message}")
        sys.exit()
    data = response.json()

    found = False
    for item in sorted(data, key=semver_key_sort, reverse=True):
        version = semver_key_sort(item)
        name = item.get('tag_name')
        if item.get('prerelease'):
            name = f"{name} (prerelease)"
        elif item.get('draft'):
            name = f"{name} (draft)"
        else:
            name = f"{name} (not-prerelease)"
        logger.debug(name)

        if version > last_seen:
            last_seen = version
            found = True
            logger.info(f"New version found: {item.get('tag_name')}")
            if last_source in ('default', 'disk'):
                with open('lastseen.txt', "w", encoding="utf-8") as file_handle:
                    file_handle.write(item.get("tag_name"))
            else:
                os.environ['LAST_SEEN'] = item.get("tag_name")
    if not found:
        logger.warning("No new version found, is still {}", last_seen)
if __name__ == "__main__":
    cli()
