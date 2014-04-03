# -*- coding: utf-8 -*-  
# Translate current string in IDA Pro

# install:
# easy_install goslate
# easy_install chardet

import struct
import re

def read_string(ea, coding=''):
    bytes = []
    if coding == 'utf-16':
        # UCS-2LE in Windows
        while Word(ea) != 0:
            bytes.append(struct.pack('H', Word(ea)))
            ea += 2
    else:
        # ANSI&UTF-8
        while Byte(ea) != 0:
            bytes.append(struct.pack('B', Byte(ea)))
            ea += 1
            
    s = ''.join(bytes)
    print 'processing:', [s]
    
    # if codepage is not given manually, anto detect
    if coding == '':
        # detect codepage
        import chardet
        codepage = chardet.detect(s)
        print 'codepage may', codepage['encoding'], \
              'confidence',   codepage['confidence']
        if codepage['confidence'] < 0.6:
            print 'Auto detect may not precise enough. Please give manually.'
            return
        coding = codepage['encoding']
        
    return s.decode(coding)
    
# call Google Translate
# sometime it would fail, try again
def google_trans(u, dstLan, dstCoding):
    s = ''
    if u:
        try:
            import goslate
            gs = goslate.Goslate()
            s = gs.translate(u, dstLan).encode(dstCoding)
        except:
            print 'translate error, try again!'
    return s

    
# arg0: current address in IDA
# arg1: soutce coding, can be auto detected. If detect result is  wrong, can be set manually. 
#       it can be utf-8/utf-16/gb2312/big5/euc-kr etc...
# arg2: dest language，default 'en'
# arg3: dest coding，default 'ascii'
def translate(ea, srcCoding='', dstLan='en', dstCoding='ascii'):
    u = read_string(ea, srcCoding)
    s = None
    if u:
        s = google_trans(u, dstLan, dstCoding)
        if s:
            Message(dstLan + ' result: ' + s + '\n')
    return s

# ------------translate fuctions------------
# ANSI、UTF-8 to English, auto detect codepage.
def trans2en():
    s = translate(ScreenEA())
    if s : MakeRptCmt(ScreenEA(), s)

# Sometime short string cannot be auto identified.
# So set manually.
# here is Chinese to English, you can change it.
def trans_cn2en():
    s = translate(ScreenEA(), 'gbk')
    if s : MakeRptCmt(ScreenEA(), s)
    
# UTF-16LE & ANSI cannot be auto identified.
# So use your eyes.
# Windows Unicode(UTF-16LE) to English
def trans2en_u():
    s = translate(ScreenEA(), 'utf-16')
    if s : MakeRptCmt(ScreenEA(), s)
#-------------------------------------

def add_hot_key(key, str_func):
    idaapi.CompileLine('static %s() { RunPythonStatement("%s()"); }'%(str_func, str_func))
    AddHotkey(key, str_func)
    
if __name__ == '__main__':
    
    # set hotkey
    add_hot_key('F3', 'trans2en');
    add_hot_key('Ctrl-F3',  'trans_cn2en');
    add_hot_key('Shift-F3', 'trans2en_u');
    
    print '-----------------------------------------'
    print 'Use F3 translate ANSI/UTF-8 to English'
    print 'Use Ctrl-F3 translate Chinese to English'
    print 'Use Shift-F3 translate Unicode to English'
    print '-----------------------------------------'
