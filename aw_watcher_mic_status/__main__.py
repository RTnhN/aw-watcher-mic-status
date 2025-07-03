import sys
import os

module_file = sys.modules[__name__].__file__
if module_file is None:
    raise RuntimeError("Module file path is not available.")

path = os.path.dirname(module_file)
path = os.path.join(path, "..")
sys.path.insert(0, path)

import aw_watcher_mic_status

aw_watcher_mic_status.main()
