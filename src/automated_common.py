#!/usr/bin/python3
# moltenform (Ben Fisher), 2019
# GPLv3

import sys
sys.path.append('bn_python_common.zip')
from bn_python_common import *

def parseArgs(ext):
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("path", help=f"A path like /home/directory or /home/file{ext}")
    parser.add_argument("--recurse", help="recurse", action="store_true")
    parser.add_argument("--test", help="run tests", action="store_true")
    parser.add_argument("--continue_on_err", help="always continue if errors occur", action="store_true")
    args = parser.parse_args()
    
    if not args.test:
        filepath = args.path
        if filepath.lower().endswith(ext):
            if not files.isfile(filepath):
                trace('not a file')
                return False, False, False, False
        else:
            if not files.isdir(filepath):
                trace('not a directory')
                return False, False, False, False
    
    return args.path, args.recurse, args.test, args.continue_on_err

def startScript(fnBefore, fn, fnCheck, fnTest, extension, scriptname):
    filepath, isRecurse, isTest, isContinue = parseArgs(extension)
    if not filepath and not isTest:
        trace('Unrecognized syntax. Run {scriptname} -h')
    elif isTest:
        fnBefore()
        fnTest()
    else:
        if isContinue:
            prefs.continueOnErr = True
            w = 'continue_on_err is good for running the script overnight, because it skips past errors ' + \
                'you should back up your input files before using it though: after running the script, ' + \
                'you need to look for errors in the log because when a "serious error" occurs the input file ' + \
                'when the error occurred will likely be deleted!'
            warn(w)
        fnBefore()
        startScriptRun(fn, fnCheck, extension, filepath, isRecurse)
    
    if prefs.errsOccurred:
        warn('warning: errors occurred. please see the log for more information.')

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
            if prefs.errsOccurred:
                warn('warning: errors occurred. please see the log for more information.')
            sys.exit(0)

def stopIfStopMarkerFound():
    markerFile = f'nocpy_request_stop'
    if files.exists(markerFile):
        trace(f'exiting because the file {markerFile} is present.')
        if prefs.errsOccurred:
            warn('warning: errors occurred. please see the log for more information.')
        sys.exit(0)

def getHumanTime():
    import time
    import datetime
    timestamp = time.time()
    value = datetime.datetime.fromtimestamp(timestamp)
    return value.strftime('%Y-%m-%d %H:%M:%S')

def addToLog(s):
    with open('nocpy_log.txt', 'a', encoding='utf8') as f:
        f.write('\n')
        f.write(getHumanTime())
        f.write(' ')
        f.write(s)

def logSeriousError(s):
    prefs.errsOccurred = True
    trace('Serious Error: ' + s)
    addToLog('Serious Error: ' + s)
    if not prefs.continueOnErr:
        sys.exit(1)

# pywinauto tips: print_control_identifiers(depth=1)
prefs = Bucket(
    maxIters = 500, # about 4 minutes
    continueOnErr = False,
    errsOccurred = False
)

