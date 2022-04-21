""" checks for new versions of handbrake """

import os
import sys
from typing import Any, Dict

import requests
from semver import Version # type: ignore
from loguru import logger

URL = "https://api.github.com/repos/Handbrake/Handbrake/releases"

RUNNING_IN_AWS = bool(os.getenv('AWS_EXECUTION_ENV'))

logger.debug(f"Running in AWS? {RUNNING_IN_AWS}")
if os.getenv('LAST_SEEN'):
    LAST_SEEN = Version.parse(os.environ['LAST_SEEN'])
    LAST_SOURCE = "env"
elif os.path.exists('lastseen.txt'):
    with open('lastseen.txt', encoding="utf-8") as file_handle:
        LAST_SEEN = Version.parse(file_handle.read().strip())
    LAST_SOURCE = "disk"
else:
    logger.debug("No last_seen set, will need to write one")
    LAST_SEEN = "0.0.0"
    LAST_SOURCE = "default"

try:
    response = requests.get(url=URL)
    response.raise_for_status()
except Exception as error_message: # pylint: disable=broad-except
    logger.error(f"Request failed: {error_message}")
    sys.exit()
data = response.json()

def semver_key_sort(value: Dict[str, Any]) -> Version:
    """ sorting function """
    parsed = Version.parse(str(value.get('tag_name')))
    return parsed


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

    if version > LAST_SEEN:
        LAST_SEEN = version.to_tuple()
        logger.info(f"New version found: {item.get('tag_name')}")
        if LAST_SOURCE in ('default', 'disk'):
            with open('lastseen.txt', "w", encoding="utf-8") as file_handle:
                file_handle.write(item.get("tag_name"))
        else:
            os.environ['LAST_SEEN'] = item.get("tag_name")
