import sys
import os

path = os.path.dirname(sys.modules[__name__].__file__)
path = os.path.join(path, "..")
sys.path.insert(0, path)

import aw_watcher_mic_status

aw_watcher_mic_status.main()
