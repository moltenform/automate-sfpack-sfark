#!/usr/bin/python3
# moltenform (Ben Fisher), 2019
# GPLv3
#
# use this tool to unpack a sfpack to a sf2 file.
#
# if you are running a 64bit python, you might see
# UserWarning: 32-bit application should be automated using 32-bit Python
# but everything still seems to work.

from automated_common import *
import os
import time

sfpackbin = r'C:\data\e4\downloads\dloads\SFPack\sfpack.exe'

def appendToAdjacentTextFile(path, s, prefix=True):
    a, b = os.path.splitext(path)
    outPath = a + '.txt'
    if prefix:
        s = "\r\n(extracted from '" + files.getname(a) + \
            ".sfpack' by Ben Fisher's automated_sfpack_decompress.py)\r\n" + s
    
    # append without changing the encoding of any existing data
    with open(outPath, 'ab') as f:
        f.write(s.encode('utf-8'))

searchFor = 'inflated by '

def getFilenamesAndCheckIfFilesAlreadyExist(s):
    assertTrue(s.lower().endswith('.sfpack'), s)
    a, b = os.path.splitext(s)
    out = a + '.sf2'
    assertTrue(not files.exists(out), 'already exists', out)
    
    # renaming because 
    # it allows easier window search
    tempname = files.getparent(s) + '\\a.sfpack'
    tempnameout = files.getparent(s) + '\\a.sf2'
    assertTrue(not files.exists(tempname), 'already exists', tempname)
    assertTrue(not files.exists(tempnameout), 'already exists', tempnameout)
    
    assertTrue(not searchFor in s)
    return s, out, tempname, tempnameout

def unpackSfpackImpl(s):
    s, out, tempname, tempnameout = getFilenamesAndCheckIfFilesAlreadyExist(s)
    
    trace('renaming', s,'\n', tempname)
    files.move(s, tempname, False)
    
    from pywinauto.application import Application
    assertTrue(not '"' in sfpackbin, sfpackbin)
    assertTrue(not '"' in tempname, tempname)
    app = Application(backend="win32").start(f'"{sfpackbin}" "{tempname}"')
    
    # allow time for app to open
    time.sleep(5) 
    
    wnd = app.window(class_name="#32770")
    if wnd and wnd.exists():
        trace("might be the Cannot Register Shell Extension dialog, don't worry, we'll close it.")
        time.sleep(1)
        wnd.type_keys('{ENTER}')
        time.sleep(1)
        
    wnd = app.window(class_name="SFPack")
    if wnd and wnd.exists():
        trace('found main window')
    else:
        assertTrue(False, 'could not find main window')
    
    # pressing the space bar starts decompression
    wnd.type_keys('{SPACE}')
    
    lookForWndTitles = ["License for a", "Licensing for a", "Information for a"]
    for lookForWndTitle in lookForWndTitles:
        time.sleep(1)
        wndinfo = app.window(title=lookForWndTitle, class_name="#32770")
        if wndinfo and wndinfo.exists():
            trace(f'Getting {lookForWndTitle}')
            assertTrue(wndinfo.edit1 and wndinfo.edit1.exists())
            theText = wndinfo.edit1.texts()
            if not theText:
                theText = ['']
            if isinstance(theText, list):
                theText = ' '.join(theText)
            appendToAdjacentTextFile(s, theText)
            time.sleep(1)
            wndinfo.type_keys('{ENTER}')
            time.sleep(1)
    
    looksFinished = False
    trace('waiting...')
    for _ in range(maxIters):
        time.sleep(0.5)
        listView = wnd.SysListView321
        assertTrue(listView and listView.exists())
        listViewText = ' '.join(listView.texts())
        if searchFor in listViewText:
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
    
    time.sleep(1)
    app.kill()
    time.sleep(1)
    files.move(tempnameout, out, False)
    return tempname, out
    
def unpackSfpack(s):
    tempname, out = unpackSfpackImpl(s)
    trace('deleting original file', tempname)
    files.delete(tempname)
    
    # always create an adjacent text file, even if there wasn't attached
    # information, just for consistency
    msg = '\r\n(' + files.getname(s) + ')'
    appendToAdjacentTextFile(s, msg, prefix=False)
    
    # don't overheat the cpu
    trace('sleeping...')
    secondsRestBetweenConversions = 5
    time.sleep(secondsRestBetweenConversions)

def runTest():
    # run these tests with "automated_sfpack_decompress.py --test"
    srcSfpack = './test/resources/sfpack'
    testdir = './test/nocpy_temp'
    files.ensure_empty_directory(testdir)
    
    # get some sfpack files for testing
    trace('setting up sfpack files into test directory...')
    for f, short in files.listfiles(srcSfpack):
        if short.lower().endswith('.sfpack'):
            files.copy(f, files.join(testdir, short), False)
    
    # convert them into sf2 files and txt files
    trace('done setting up sf2 files into test directory')
    sys.argv = [__file__, testdir]
    startScript(unpackSfpack, getFilenamesAndCheckIfFilesAlreadyExist, runTest, '.sfpack', files.getname(__file__))
    trace(f'test complete. if you look at {testdir}, all sfpack files should have been converted to sf2.')
    if getInputBool('delete temp files now?'):
        files.ensure_empty_directory(testdir)

def go():
    warn('if an error msg shows up saying "Could not register shell extension", this is fine - we can work around it.')
    checkPrereq(sfpackbin, 'sfpack.exe')
    startScript(unpackSfpack, getFilenamesAndCheckIfFilesAlreadyExist, runTest, '.sfpack', files.getname(__file__))

if __name__=='__main__':
    go()
    
