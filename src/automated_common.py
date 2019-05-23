#!/usr/bin/python3
# moltenform (Ben Fisher), 2019
# GPLv3

import sys
sys.path.append('bn_python_common.zip')
from bn_python_common import *

def parseArgs(args, ext):
    isTest = False
    isRecurse = False
    if len(args) == 3 and args[2] == '--recurse':
        isRecurse = True
    elif len(args) == 2 and args[1] == '--test':
        isTest = True
        return False, isRecurse, isTest
    elif len(args) != 2:
        return False, False, False
    
    filepath = args[1]
    if filepath.lower().endswith(ext):
        if not files.isfile(filepath):
            trace('not a file')
            return False, False, False
    else:
        if not files.isdir(filepath):
            trace('not a directory')
            return False, False, False
    
    return filepath, isRecurse, isTest

def startScript(fn, fnCheck, fnTest, extension, scriptname):
    args = sys.argv
    filepath, isRecurse, isTest = parseArgs(args, extension)
    if not filepath and not isTest:
        trace('Unrecognized syntax. Try something like:')
        trace(f'{scriptname} /home/file{extension}')
        trace(f'{scriptname} /home/directory')
        trace(f'{scriptname} /home/directory --recurse')
    elif isTest:
        fnTest()
    else:
        startScriptRun(fn, fnCheck, extension, filepath, isRecurse)

def startScriptRun(fn, fnCheck, extension, filepath, isRecurse):
    # check that pywinauto is installed
    try:
        from pywinauto.application import Application
    except:
        trace("Could not start pywinauto")
        trace("try running 'pip install pywinauto'")
        sys.exit(0)
    
    # if given a single file, just run that
    if files.isfile(filepath):
        fnCheck(filepath)
        fn(filepath)
        return
    
    # check all the files, helps catch any errors early
    trace('checking all files...')
    fnIter = files.recursefiles if isRecurse else files.listfiles
    for f, short in fnIter(filepath):
        if short.lower().endswith(extension):
            fnCheck(f)
            
    # process all the files
    trace('processing all files...')
    fnIter = files.recursefiles if isRecurse else files.listfiles
    for f, short in fnIter(filepath):
        if short.lower().endswith(extension):
            stopIfStopMarkerFound()
            fn(f)

def checkPrereq(binpath, binname, website=None):
    if not files.isfile(binpath):
        trace(f"Could not find '{binpath}'")
        trace(f"Please update the python script with the right path to '{binname}'")
        if website:
            trace(f"You can probably find this here: {website}")
        sys.exit(0)

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

def stopIfStopMarkerFound():
    markerFile = f'nocpy_request_stop'
    if files.exists(markerFile):
        trace(f'exiting because the file {markerFile} is present.')
        sys.exit(0)

# pywinauto tips: print_control_identifiers(depth=1)
maxIters = 10000
