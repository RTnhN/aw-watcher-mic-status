aw-watcher-template
==================

This is a template watcher for [ActivityWatch](https://github.com/ActivityWatch/activitywatch). It can be used as a starting point for creating your own watchers. Before you use it, make sure that you remove all the references to `aw-watcher-template` in the code. This will include the the folder names as well as the name of the package. You can do this by doing a global search and replace for `aw-watcher-template` with the name of your watcher.

This watcher is currently in a early stage of development, please submit PRs if you find bugs!


## Usage

### Step 0: Do Something like setup an API key 

### Step 1: Install package

Install the requirements:

```sh
pip install .
```

First run (generates config):
```sh
python aw-watcher-template/main.py
```

### Step 2: Enter config

Make sure to describe what types of config you need to do in the config file. 


### Step 3: Restart the server and enable the watcher

Don't forget to add it to the aw-qt.toml file so that it gets started automatically when AW starts. 