# moltenform (Ben Fisher), 2019
# GPLv3

from ben_python_common import *
import os
import time

sfarkbin = r'C:\data\e4\downloads\dloads\SFPack\sfarkbinaries\sfArk.exe'
sfarkxtc = r'C:\data\e2\d_1\repos\sfarkxtc\sfarkxtc-windows-3.0b-win64\sfarkxtc-windows-3.0b-win64\sfarkxtc.exe'

# note: before running, recommend that you change sfark.exe Preferences to say:
# compression level Maximum
# include notes-never, include license-never
# when opening a file, start Compression (i think this is the default)

# might print a warning
# UserWarning: 32-bit application should be automated using 32-bit Python
# but it still seems to work.

def runSfarkXtc(sin, sout):
    assertTrue(sin.lower().endswith('.sfark'), sin)
    assertTrue(sout.lower().endswith('.sf2'), sout)
    assertTrue(not files.exists(sout), sout)
    args = [sfarkxtc, sin, sout, '--quiet']
    files.run(args)
    assertTrue(files.exists(sout), sout)
    
def makeSfark(s):
    assertTrue(s.lower().endswith('.sf2'), s)
    a,b = os.path.splitext(s)
    out = a + '.sfark'
    assertTrue(not files.exists(out), 'already exists', out)
    
    # renaming because 
    # 1) sfark chokes on complex filenames
    # 2) allows easier window search
    tempname = files.getparent(s) + '\\a.sf2'
    tempnameout = files.getparent(s) + '\\a.sfark'
    assertTrue(not files.exists(tempname), 'already exists', tempname)
    assertTrue(not files.exists(tempnameout), 'already exists', tempnameout)
    trace('renaming', s,'\n', tempname)
    files.move(s, tempname, False)
    
    from pywinauto.application import Application
    #~ app = Application(backend="uia").start([sfarkbin, s])
    #~ app = Application(backend="uia").start(f'"{sfarkbin}" "{tempname}"')
    assertTrue(not '"' in sfarkbin, sfarkbin)
    assertTrue(not '"' in tempname, tempname)
    app = Application(backend="win32").start(f'"{sfarkbin}" "{tempname}"')
    
    assertTrue(not 'Compressing ' in s, s)
    
    time.sleep(5) # wait for the app to be launched/compression started
    
    looksFinished = False
    for _ in range(9999999):
        time.sleep(0.5)
        subwindow = app.window(title='Compressing a.sf2...')
        
        if not subwindow or not subwindow.exists():
            looksFinished = True
            print('looks done')
            break
        else:
            print('window still there, waiting')
        
    if not looksFinished:
        assertTrue(False, s, 'timed out')
    if not files.exists(tempnameout):
        assertTrue(False, s, 'did not see')
    if not files.getsize(tempnameout) > 100:
        assertTrue(False, s, 'size is suspiciously small')
        
    files.move(tempnameout, out, False)
    
    time.sleep(1)
    app.kill()
    return tempname, out

def startSafelyConvertSf2ToSfark(s):
    expectChecksum = files.computeHash(s, 'md5')
    assertTrue(s.lower().endswith('.sf2'), s)
    tempname, out = makeSfark(s)
    tempUnpackName = files.join(files.getparent(s), 'tmpUnpack.sf2')
    runSfarkXtc(out, tempUnpackName)
    checkSumOut = files.computeHash(tempUnpackName, 'md5')
    assertEq(expectChecksum, checkSumOut, s)
    trace('confirm match', expectChecksum, checkSumOut)
    trace('deleting', tempUnpackName)
    trace('deleting', tempname)
    #~ files.delete(tempUnpackName)
    #~ files.delete(tempname)

if __name__=='__main__':
    # use print_control_identifiers(depth=4) to investigate
    startSafelyConvertSf2ToSfark(r'C:\data\e4\downloads\dloads\allsf\SoundFonts - The Collection\SoundFont Project\SoundFonts\[SF2] Bass Ibanez Roadstar II Picked (25,398KB).sf2')
    #~ go()
    