#!/usr/bin/env python3

import sys
import logging
import traceback
from time import sleep
from datetime import datetime, timezone

from aw_core import dirs
from aw_core.models import Event
from aw_client.client import ActivityWatchClient

from .helper.mic_checker import is_mic_active


class StatusLinePrinter:
    _last_msg_length = 0

    def print(self, msg: str) -> None:
        print(" " * self._last_msg_length, end="\r")
        print(msg, end="\r")
        self._last_msg_length = len(msg)


printer = StatusLinePrinter()


watcher_name = "aw-watcher-mic-status"

logger = logging.getLogger(watcher_name)
DEFAULT_CONFIG = f"""
[{watcher_name}]
poll_time = 0.5
"""


def load_config():
    from aw_core.config import load_config_toml as _load_config

    return _load_config(watcher_name, DEFAULT_CONFIG)


def main():
    logging.basicConfig(level=logging.INFO)

    config_dir = dirs.get_config_dir(watcher_name)

    config = load_config()
    poll_time = float(config[watcher_name].get("poll_time", None))
    if poll_time is None:
        print("poll_time is not set in the config file.")
        print(f"You can set it in {config_dir}")
        sys.exit(1)

    # TODO: Fix --testing flag and set testing as appropriate
    aw = ActivityWatchClient(watcher_name, testing=False)
    bucketname = "{}_{}".format(aw.client_name, aw.client_hostname)
    if aw.get_buckets().get(bucketname) == None:
        aw.create_bucket(bucketname, event_type="mic_status_data", queued=True)
    aw.connect()

    # This is the maximum time that the action will take.
    # If the action takes longer than this, the event will be split into multiple events.
    # Make sure to make this number as big as needed to make sure that the event is not split.
    max_action_time = 0.5

    while True:

        try:
            title = "Mic off"
            state, name = is_mic_active()
            if state:
                title = "Mic on"
            data = {"title": title, "active_name": name}
            printer.print(name)
            event = Event(timestamp=datetime.now(timezone.utc), data=data)
            aw.heartbeat(
                bucketname, event, pulsetime=poll_time + max_action_time, queued=True
            )
        except Exception as e:
            print("An exception occurred: {}".format(e))
            traceback.print_exc()
        sleep(poll_time)


if __name__ == "__main__":
    main()
