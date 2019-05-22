# moltenform (Ben Fisher), 2019
# GPLv3

import sys
sys.path.append('bn_python_common.zip')
from bn_python_common import *

def initCheckPyWinAuto():
    pass

def userConfirmPrefsSet(desc, markerfile):
    if not files.exists(markerfile):
        trace(desc)

