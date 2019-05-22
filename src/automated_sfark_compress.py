#!/usr/bin/python3
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

from automated_common import *
import os
import time

# set this to False to skip verification with sfarkxtc
useSfarkXtcToConfirmIntegrity = True

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
    files.run(args)
    assertTrue(files.exists(sout), sout)

searchFor = 'Compressing '

def getFilenamesAndCheckIfFilesAlreadyExist(s):
    assertTrue(s.lower().endswith('.sf2'), s)
    a,b = os.path.splitext(s)
    out = a + '.sfark'
    assertTrue(not files.exists(out), 'already exists', out)
    
    # make a simpler filename because 
    # 1) sfark shows error dialog on complex filenames
    # 2) allows easier window search
    tempname = files.getparent(s) + '\\a.sf2'
    tempnameout = files.getparent(s) + '\\a.sfark'
    tempnameunpack = files.getparent(s) + '\\tmpUnpack.sf2'
    assertTrue(not files.exists(tempname), 'already exists', tempname)
    assertTrue(not files.exists(tempnameout), 'already exists', tempnameout)
    assertTrue(not files.exists(tempnameunpack), 'already exists', tempnameunpack)
    
    assertTrue(not searchFor in s, f"we don't support filepaths that contain {searchFor}", s)
    return s, out, tempname, tempnameout

def compressToSfark(s):
    s, out, tempname, tempnameout = getFilenamesAndCheckIfFilesAlreadyExist(s)
    trace('renaming', s,'\n', tempname)
    files.move(s, tempname, False)
    
    from pywinauto.application import Application
    assertTrue(not '"' in sfarkbin, sfarkbin)
    assertTrue(not '"' in tempname, tempname)
    app = Application(backend="win32").start(f'"{sfarkbin}" "{tempname}"')
    
    # wait for the app to be launched/compression started
    time.sleep(5)
    
    looksFinished = False
    trace('waiting...')
    for _ in range(maxIters):
        time.sleep(0.5)
        subwindow = app.window(title='Compressing a.sf2...')
        if not subwindow or not subwindow.exists():
            looksFinished = True
            print('looks done')
            break
        else:
            print('.', end='', flush=True)
        
    if not looksFinished:
        assertTrue(False, s, 'timed out')
    if not files.exists(tempnameout):
        assertTrue(False, s, 'did not see')
    if not files.getsize(tempnameout) > 100:
        assertTrue(False, s, 'size is suspiciously small')
        
    files.move(tempnameout, out, False)
    time.sleep(1)
    app.kill()
    time.sleep(1)
    return tempname, out

def startSafelyConvertSf2ToSfark(s):
    checkBeforeRun(warnBeforeRun, files.getname(__file__))
    
    expectChecksum = files.computeHash(s, 'md5')
    assertTrue(s.lower().endswith('.sf2'), s)
    tempname, out = compressToSfark(s)
    if useSfarkXtcToConfirmIntegrity:
        tempUnpackName = files.join(files.getparent(s), 'tmpUnpack.sf2')
        if files.exists(tempUnpackName):
            softDeleteFile(tempUnpackName)

        runSfarkXtc(out, tempUnpackName)
        checkSumOut = files.computeHash(tempUnpackName, 'md5')
        trace('verifying match', expectChecksum, checkSumOut)
        assertEq(expectChecksum, checkSumOut, s, tempUnpackName)
        trace('deleting temporary file', tempUnpackName)
        files.delete(tempUnpackName)
    trace('deleting temporary file', tempname)
    files.delete(tempname)
    
    # don't overheat the cpu
    secondsRestBetweenConversions = 10
    time.sleep(secondsRestBetweenConversions)

def runTest():
    # run these tests with "automated_sfark_compress.py --test"
    srcSfark = r'C:\data\e2\d_1\repos\sfarkxtc\sfarkxtc-windows\src\test\sfarks\lvl4'
    testdir = r'C:\data\e2\d_1\repos\sfarkxtc\automate-sfpack-sfark\src\nocpy_test\sf2'
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
    startScript(startSafelyConvertSf2ToSfark, getFilenamesAndCheckIfFilesAlreadyExist, runTest, '.sf2', files.getname(__file__))

def go():
    checkPrereq(sfarkbin, 'sfark.exe')
    if useSfarkXtcToConfirmIntegrity:
        checkPrereq(sfarkxtcbin, 'sfarkxtc.exe', 'https://github.com/moltenform/sfarkxtc-windows')
    
    startScript(startSafelyConvertSf2ToSfark, getFilenamesAndCheckIfFilesAlreadyExist, runTest, '.sf2', files.getname(__file__))

if __name__=='__main__':
    go()
