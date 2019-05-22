#!/usr/bin/python3
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

def parseArgs(args, ext):
    isRecurse = False
    if len(args) == 3 and args[2] == '--recurse':
        isRecurse = True
    elif len(args) != 2:
        return False, False
    
    filepath = args[1]
    if filepath.lower().endswith(ext):
        if not files.isfile(filepath):
            trace('not a file')
            return False, False
    else:
        if not files.isdir(filepath):
            trace('not a directory')
            return False, False
    
    return filepath, isRecurse

def startScript(fn, extension, scriptname):
    args = sys.argv
    filepath, isRecurse = parseArgs(args, extension)
    if not filepath:
        trace(f'Example Syntax: {scriptname} /home/file{extension}')
        trace(f'Example Syntax: {scriptname} /home/directory')
        trace(f'Example Syntax: {scriptname} /home/directory --recurse')
    else:
        startScriptRun(fn, extension, filepath, isRecurse)

def startScriptRun(fn, extension, filepath, isRecurse):
    if files.isfile(filepath):
        fn(filepath)
        return
        
    fnIter = files.recursefiles if isRecurse else files.listfiles
    for f, short in fnIter(filepath):
        if short.lower().endswith(extension):
            fn(f)

def checkBeforeRun(warnBeforeRun, scriptname):
    withoutExt = files.getname(scriptname).split('.')[0]
    markerFile = f'.has_seen_msg_{withoutExt}'
    if not files.exists(markerFile):
        trace(warnBeforeRun)
        isContinue = getInputBool('Continue?')
        if isContinue:
            files.writeall(markerFile, '', 'w')
        else:
            sys.exit(0)

maxIters = 10000
