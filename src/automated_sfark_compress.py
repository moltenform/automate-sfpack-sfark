#!/usr/bin/env python3
# moltenform (Ben Fisher), 2019
# GPLv3
#
# use this tool to *safely* compress a .sf2 to a .sfark
# it runs sfark.exe and drives its ui, then
# the open-source sfarkxtc tool confirms that the
# input and output are 100% identical.
#
# if you are running a 64bit python, you might see
# UserWarning: 32-bit application should be automated using 32-bit Python
# but everything still seems to work.
#
#

from automated_common import *
import os
import time

# set this to False to skip verification with sfarkxtc
useSfarkXtcToConfirmIntegrity = True

# download sfarkxtc.exe from 'releases' at https://github.com/moltenform/sfarkxtc-windows
sfarkbin = r'C:\data\e4\downloads\dloads\SFPack\sfarkbinaries\sfArk.exe'
sfarkxtcbin = r'C:\data\e2\d_1\repos\sfarkxtc\sfarkxtc-windows-3.0b-win64\sfarkxtc-windows-3.0b-win64\sfarkxtc.exe'

warnBeforeRun = '''
note: before running, I recommend that you
copy sfark.exe to a writable directory (not program files)
open sfark.exe, open File->Preferences, and change the following:
Open tab "when compressing..."
compression level 4:Maximum
include notes-never
include license-never
enable hide tips
Open tab "General"
confirm that Associated-file launch + Process files immediately is checked,
and nothing else
'''

def runSfarkXtc(sin, sout):
    assertTrue(sin.lower().endswith('.sfark'), sin)
    assertTrue(sout.lower().endswith('.sf2'), sout)
    assertTrue(not files.exists(sout), sout)
    
    args = [sfarkxtcbin, sin, sout, '--quiet']
    try:
        if files.getsize(sin) > 100:
            files.run(args)
        else:
            logSeriousError('input file size is too small, probably an invalid file')
    except:
        errInfo = str(sys.exc_info())
        logSeriousError('sfarkxtc failed to run')
        logSeriousError(errInfo)

    if not files.exists(sout):
        # log the error, and write a small placeholder file so that we can continue
        # running as if it had completed as expected
        logSeriousError('sfarkxtc did not make an output file')
        files.writeall(sout, '(placeholder)', 'w')

searchFor = 'Compressing '

def getFilenamesAndCheckIfFilesAlreadyExist(s):
    assertTrue(s.lower().endswith('.sf2'), s)
    a,b = os.path.splitext(s)
    out = a + '.sfark'
    assertTrue(not files.exists(out), 'already exists', out)
    
    # make a simpler filename because 
    # 1) sfark shows error dialog on complex filenames
    # 2) allows easier window search
    # 3) avoids potential problems with unicode chars
    tempname = files.getparent(s) + '\\a.sf2'
    tempnameout = files.getparent(s) + '\\a.sfark'
    tempnameunpack = files.getparent(s) + '\\tmpUnpack.sf2'
    assertTrue(not files.exists(tempname), 'already exists', tempname)
    assertTrue(not files.exists(tempnameout), 'already exists', tempnameout)
    assertTrue(not files.exists(tempnameunpack), 'already exists', tempnameunpack)
    
    assertTrue(not searchFor in s, f"we don't support filepaths that contain {searchFor}", s)
    return s, out, tempname, tempnameout

def compressToSfarkImpl(s):
    addToLog(f'compressToSfarkImpl {s}')
    s, out, tempname, tempnameout = getFilenamesAndCheckIfFilesAlreadyExist(s)
    trace('renaming', s,'\n', tempname)
    files.move(s, tempname, False)
    
    state = Bucket(looksFinished=False, app=None)
    try:
        runPywinAuto(state, s, out, tempname, tempnameout)
    except:
        errInfo = str(sys.exc_info())
        logSeriousError(f'failure while automating {sfarkbin}')
        logSeriousError(errInfo)
    
    try:
        # pause while killing app, to make sure app has time to release file locks
        time.sleep(1)
        if state.app:
            state.app.kill()
        time.sleep(1)
    except:
        errInfo = str(sys.exc_info())
        logSeriousError(f'failure while running app.kill()')
        logSeriousError(errInfo)
    
    if not state.looksFinished:
        logSeriousError('timed out')
    if not files.exists(tempnameout):
        # log the error, and write a small placeholder file so that we can continue
        # running as if it had completed as expected
        logSeriousError('did not see output')
        files.writeall(tempnameout, '(placeholder)', 'w')
    if not files.getsize(tempnameout) > 100:
        logSeriousError('size is suspiciously small')
    files.move(tempnameout, out, False)
    return tempname, out

def runPywinAuto(state, s, out, tempname, tempnameout):
    if not files.getsize(tempname) > 100:
        logSeriousError('input file size is too small, probably an invalid file')
        return True
        
    from pywinauto.application import Application
    assertTrue(not '"' in sfarkbin, sfarkbin)
    assertTrue(not '"' in tempname, tempname)
    state.app = Application(backend="win32").start(f'"{sfarkbin}" "{tempname}"')

    # wait for the app to be launch and start compression
    time.sleep(5)

    trace('waiting...')
    for _ in range(prefs.maxIters):
        time.sleep(0.5)
        wnd = state.app.window(title='Compressing a.sf2...')
        if not wnd or not wnd.exists():
            state.looksFinished = True
            print('looks done')
            break
        else:
            print('.', end='', flush=True)

def compressToSfark(s):
    checkBeforeRun(warnBeforeRun, files.getname(__file__))
    
    expectChecksum = files.computeHash(s, 'md5')
    assertTrue(s.lower().endswith('.sf2'), s)
    tempname, out = compressToSfarkImpl(s)
    if useSfarkXtcToConfirmIntegrity:
        tempUnpackName = files.join(files.getparent(s), 'tmpUnpack.sf2')
        if files.exists(tempUnpackName):
            softDeleteFile(tempUnpackName)

        runSfarkXtc(out, tempUnpackName)
        checkSumOut = files.computeHash(tempUnpackName, 'md5')
        trace('verifying match', expectChecksum, checkSumOut)
        if expectChecksum != checkSumOut:
            logSeriousError(f'checksum mismatch!!! {expectChecksum} {checkSumOut}')
        
        trace('deleting temporary file', tempUnpackName)
        files.delete(tempUnpackName)
    trace('deleting original file', tempname)
    files.delete(tempname)
    
    # don't overheat the cpu
    trace('sleeping...')
    secondsRestBetweenConversions = 10
    stopIfStopMarkerFound()
    time.sleep(secondsRestBetweenConversions)
    stopIfStopMarkerFound()

def recurseSfpackToSfark(dir):
    prefs.continueOnErr = True
    import automated_sfpack_decompress
    for f, short in files.recursefiles(dir):
        if short.lower().endswith('.sfpack'):
            automated_sfpack_decompress.getFilenamesAndCheckIfFilesAlreadyExist(f)
            getFilenamesAndCheckIfFilesAlreadyExist(f.replace('.sfpack', '.sf2'))
            
    for f, short in files.recursefiles(dir):
        if short.lower().endswith('.sfpack'):
            stopIfStopMarkerFound()
            sf2 = automated_sfpack_decompress.unpackSfpack(f)
            addToLog('md5 checksum=' + files.computeHash(sf2, 'md5'))
            compressToSfark(sf2)
    
    if prefs.errsOccurred:
        warn('warning: errors occurred. please see the log for more information.')


def runTest():
    # run these tests with "automated_sfark_compress.py --test"
    srcSfark = './test/resources/sfark'
    testdir = './test/nocpy_temp'
    files.ensure_empty_directory(testdir)
    
    # get some sf2 files for testing
    trace('setting up sf2 files into test directory...')
    for f, short in files.listfiles(srcSfark):
        if short.lower().endswith('.sfark'):
            out = files.join(testdir, short.lower().replace('.sfark', '.sf2'))
            assertTrue(not files.exists(out))
            runSfarkXtc(f, out)
    
    # convert them into sfarks
    trace('done setting up sf2 files into test directory')
    sys.argv = [__file__, testdir]
    startScript(lambda: 0, compressToSfark, getFilenamesAndCheckIfFilesAlreadyExist, runTest, '.sf2', files.getname(__file__))
    trace(f'test complete. if you look at {testdir}, all sf2 files should have been converted to sfark.')
    if getInputBool('delete temp files now?'):
        files.ensure_empty_directory(testdir)

def checkPrereqsBeforeRun():
    checkPrereq(sfarkbin, 'sfark.exe')
    if useSfarkXtcToConfirmIntegrity:
        checkPrereq(sfarkxtcbin, 'sfarkxtc.exe', '"releases" at https://github.com/moltenform/sfarkxtc-windows')

def go():
    startScript(checkPrereqsBeforeRun, compressToSfark,
        getFilenamesAndCheckIfFilesAlreadyExist, runTest,
        '.sf2', files.getname(__file__))

if __name__=='__main__':
    go()
