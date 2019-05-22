#!/usr/bin/python3
# moltenform (Ben Fisher), 2019
# GPLv3
#
# use this tool to unpack a sfpack to a 
#
# if you are running a 64bit python, you might see
# UserWarning: 32-bit application should be automated using 32-bit Python
# but everything still seems to work.

from automated_common import *
import os
import time

sfpackbin = r'C:\data\e4\downloads\dloads\SFPack\SFPACK.EXE'


def appendToTextFile(path, s):
    a, b = os.path.splitext(path)
    outPath = a + '.txt'

    s = "\r\n(extracted from '" + files.getname(a) + \
        ".sfpack' by Ben Fisher's automated_sfpack_unpack.py)\r\n" + s
    
    # append without changing encoding of any existing data
    with open(outPath, 'ab') as f:
        f.write(s.encode('utf-8'))

def startUnsfpack(s):
    assertTrue(s.lower().endswith('.sfpack'), s)
    a,b = os.path.splitext(s)
    out = a + '.sf2'
    assertTrue(not files.exists(out), 'already exists', out)
    
    # renaming because 
    # it allows easier window search
    tempname = files.getparent(s) + '\\a.sfpack'
    tempnameout = files.getparent(s) + '\\a.sf2'
    assertTrue(not files.exists(tempname), 'already exists', tempname)
    assertTrue(not files.exists(tempnameout), 'already exists', tempnameout)
    trace('renaming', s,'\n', tempname)
    files.move(s, tempname, False)
    
    from pywinauto.application import Application
    assertTrue(not '"' in sfpackbin, sfpackbin)
    assertTrue(not '"' in tempname, tempname)
    app = Application(backend="win32").start(f'"{sfpackbin}" "{tempname}"')
    
    time.sleep(2) # allow time for app to open
    #~ wnd = app.window(title='SFPack')
    #~ if not wnd or not wnd.exists():
        #~ assertTrue(False, 'wnd not found', s)
    
    #~ stuff = str(wnd.print_control_identifiers(depth=1))
    #~ if 'class_name="#32770"' in stuff:
    aa = app.window(class_name="#32770")
    if aa and aa.exists():
        trace('looks like the Cannot Register error')
        time.sleep(1)
        aa.type_keys('{ENTER}')
        time.sleep(1)
        
    aa = app.window(class_name="SFPack")
    if aa and aa.exists():
        trace('cool found main window')
    else:
        assertTrue(False, 'could not find main window')
    
    aa.type_keys('{SPACE}')
    
    
    lookFor = ["Information for a", "License for a", "Licensing for a"]
    for t in lookFor:
        time.sleep(1)
        aainfo = app.window(title=t)
        if aainfo and aainfo.exists():
            trace('Getting Information for a')
            assertTrue(aainfo.edit1 and aainfo.edit1.exists())
            theText = aainfo.edit1.texts()
            theText = ''.join(theText)
            appendToTextFile(s, theText)
            time.sleep(1)
            aainfo.type_keys('{ENTER}')
            time.sleep(1)
    
    searchFor = 'inflated by '
    assertTrue(not searchFor in s)
    
    looksFinished = False
    for _ in range(maxIters):
        time.sleep(0.5)
        listView = aa.SysListView321
        assertTrue(listView and listView.exists())
        listViewText = ' '.join(listView.texts())
        if searchFor in listViewText:
            looksFinished = True
            trace('looks done')
            break
        else:
            trace('still waiting')
            
    if not looksFinished:
        assertTrue(False, s, 'timed out')
    if not files.exists(tempnameout):
        assertTrue(False, s, 'did not see')
    if not files.getsize(tempnameout) > 100:
        assertTrue(False, s, 'size is suspiciously small')
    
    time.sleep(1)
    app.kill()
    return tempname, tempnameout, out
    
def startUnsfpackAll(s):
    tempname, tempnameout, out = startUnsfpack(s)
    files.move(tempname, s, False)
    files.move(tempnameout, out, False)

def tmpTest():
    if files.exists(r'C:\data\e2\d_1\repos\sfarkxtc\automate-sfpack-sfark\nocpy_test\a.sfpack'):
        files.move(r'C:\data\e2\d_1\repos\sfarkxtc\automate-sfpack-sfark\nocpy_test\a.sfpack', r'C:\data\e2\d_1\repos\sfarkxtc\automate-sfpack-sfark\nocpy_test\hh.sfpack', False)
    startUnsfpack(r'C:\data\e2\d_1\repos\sfarkxtc\automate-sfpack-sfark\nocpy_test\hh.sfpack')

def go():
    startScript(startUnsfpackAll, '.sfpack', files.getname(__file__))

if __name__=='__main__':
    go()
    
