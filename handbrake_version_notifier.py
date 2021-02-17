#!/usr/bin/env python3

import os
import sys
import requests
from semver import Version

os.environ['LOGURU_LEVEL'] = "INFO"
from loguru import logger


URL = "https://api.github.com/repos/Handbrake/Handbrake/releases"

RUNNING_IN_AWS = True if os.getenv('AWS_EXECUTION_ENV', False) else False

logger.debug(f"Running in AWS? {RUNNING_IN_AWS}")
if os.getenv('LAST_SEEN'):
    LAST_SEEN = Version.parse(os.getenv('LAST_SEEN'))
    LAST_SOURCE = "env"
elif os.path.exists('lastseen.txt'):
    LAST_SEEN = Version.parse(open('lastseen.txt', 'r').read().strip())
    LAST_SOURCE = "disk"
else:
    logger.debug("No last_seen set, will need to write one")
    LAST_SEEN = "0.0.0"
    LAST_SOURCE = "default"

try:
    response = requests.get(url=URL)
    response.raise_for_status()
except Exception as error_message:
    logger.error(f"Request failed: {error_message}")
    sys.exit()
data = response.json()

def semver_key_sort(value):
    parsed = Version.parse(value.get('tag_name'))
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
            with open('lastseen.txt', "w") as fh:
                fh.write(item.get("tag_name"))
        else:
            os.env['LAST_SEEN'] = item.get("tag_name")

