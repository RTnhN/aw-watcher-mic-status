#!/usr/bin/env python3

import logging
import traceback
from time import sleep
from datetime import datetime, timezone

from aw_core import dirs
from aw_core.models import Event
from aw_client.client import ActivityWatchClient

from .helper.mic_checker import is_mic_active


watcher_name = "aw-watcher-mic-status"

logger = logging.getLogger(watcher_name)
DEFAULT_CONFIG = f"""
[{watcher_name}]
poll_time = 0.5
"""
def load_config():
    from aw_core.config import load_config_toml as _load_config
    return _load_config(watcher_name, DEFAULT_CONFIG)

def print_statusline(msg):
    last_msg_length = (
        len(print_statusline.last_msg) if hasattr(print_statusline, "last_msg") else 0
    )
    print(" " * last_msg_length, end="\r")
    print(msg, end="\r")
    print_statusline.last_msg = msg

def main():
    logging.basicConfig(level=logging.INFO)

    config_dir = dirs.get_config_dir(watcher_name)

    config = load_config()
    poll_time = float(config[watcher_name].get("poll_time"))

    # TODO: Fix --testing flag and set testing as appropriate
    aw = ActivityWatchClient(watcher_name, testing=False)
    bucketname = "{}_{}".format(aw.client_name, aw.client_hostname)
    if aw.get_buckets().get(bucketname) == None:
        aw.create_bucket(bucketname, event_type="mic_status_data", queued=True)
    aw.connect()

    # This is the maximum time that the action will take. 
    # If the action takes longer than this, the event will be split into multiple events.
    # Make sure to make this number as big as needed to make sure that the event is not split.
    max_action_time = .5

    while True:

        try:
            title =  f"Mic off"
            if is_mic_active():
                title =  f"Mic on"
            data = {"title": title}
            print_statusline(title)
            event = Event(timestamp=datetime.now(timezone.utc), data=data)
            aw.heartbeat(bucketname, event, pulsetime=poll_time + max_action_time, queued=True)
        except Exception as e:
            print("An exception occurred: {}".format(e))
            traceback.print_exc()
        sleep(poll_time)


if __name__ == "__main__":
    main()
