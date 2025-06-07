aw-watcher-mic-status
==================

This is a watcher that checks if a mic is active or not. It does not save any audio. This can be great to check if you had a meeting during a period of time or if you were playing a game online.

This watcher is currently in a early stage of development, please submit PRs if you find bugs! I have only tested this on windows. Please let me know if you have tested it on other OS's such as macOS or Linux.


## Usage

### Step 1: Install package

Install the requirements:

```sh
pip install .
```

First run (generates config):
```sh
python aw-watcher-mic-status/main.py
```

### Step 2: Enter config

The only thing that you might need to change is the poll time. This is the time that the checking loop will run. 


### Step 3: Restart the server and enable the watcher

Don't forget to add it to the aw-qt.toml file so that it gets started automatically when AW starts. 