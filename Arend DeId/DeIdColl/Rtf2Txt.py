'''
Copyright (C) 2012 Raullen Chai

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import DeIdColl.RtfParser as RtfParser

class Destination:
    def __init__(self,foutput,parser):
        self.foutput = foutput
        self.name = 'Destination'
        self.parser = parser
        self.ansicpg = None

    def __repr__(self):
        return self.name
    
    def putChar(self,str2):
        pass

    def doControl(self,token,arg):
        pass

    def pushState(self,list2):
        list2.append(self)

    def popState(self,list2):
        list2.pop()

    def close(self):
        pass

class RtfDestination(Destination):
    def __init__(self, foutput, parser, fontTable=None, colorTable=None):
        Destination.__init__(self, foutput, parser)
        self.name = 'Rtf'
        self.fontCounter = 0
        self.styles = ['']
        self.italic = False
        if fontTable:
            self.fontTable = fontTable
        else:
            self.fontTable = FontTableDestination(self.foutput,self.parser)
        if colorTable:
            self.colorTable = colorTable
        else:
            self.colorTable = ColorTableDestination(self.foutput,self.parser)
        self.characterSet = None
        self.ansicpg = None
        self.reset()

    def reset(self):
        self.close()
    
    def doControl(self,token,arg):
        if token in ['*','stylesheet','info']:
            #skip everything
            self.parser.setDest(Destination(self.foutput,self.parser))
        elif token == 'rtf':
            pass
        elif token in ['ansi','mac','pc','pca']:
            self.characterSet = token
            if token == 'pc':
                self.ansicpg = '437'
            elif token == 'pca':
                self.ansicpg = '850'
        elif token == 'ansicpg':
            self.ansicpg = arg
        elif token == 'fonttbl':
            self.parser.setDest(self.fontTable)
        elif token == 'colortbl':
            self.parser.setDest(self.colorTable)
        elif token == 'par':
            self.foutput.write('\n')
        elif token == 'tab':
            self.foutput.write('\t')
        elif token in  ('b','i','strike','ql','qr','qj','qc'):
            #bold italic strike
            #open = self.tags[token][0]
            #close = self.tags[token][1]
            #self.treatIt(token,arg,open,close)
            pass
        elif token == 'ul':
            #underline
            self.styles.append('ul')
        elif token == 'ulnone':
            self.styles.pop()
        elif token == 'fs':
            #font size
            if self.styles and self.styles[-1] == 'fs':
                self.styles.pop()
            size = int(arg) / 2
            size = size - 9
            if size >= 0:
                size = '+' + str(size)
            else:
                size = str(size)
            self.styles.append('fs')
        #elif token == 'f':
            #font
            #font = self.fontTable.getFont(int(arg))
        #elif token == 'cf':
            #foreground color
            #color = self.colorTable.getColor(int(arg) - 1)
            #if self.styles and self.styles[-1] == 'cf':
            #    self.styles.pop()
            #self.styles.append('cf')
        elif token in  ['pard','plain']:
            self.reset()
        else:
            #skip unknown tag
            #print token, arg
            pass

    def treatIt(self,token,arg,open2,close):
        toggle = getattr(self,token)
        if toggle:
            self.foutput.write(close)
            self.styles.pop()
        else:
            self.foutput.write(open2)
            self.styles.append(token)
        setattr(self,token,not toggle)

    def putChar(self,str2):
        str2.replace('\r','\n')
        self.foutput.write(str2)

    def close(self):
        #close all pending types
        #foutput = self.foutput
        styles = self.styles
        styles.reverse()
        self.styles = ['']

    def pushState(self,list2):
        newRtf = RtfDestination(self.foutput, self.parser, self.fontTable, self.colorTable)
        list2.append(newRtf)

    def popState(self,list2):
        self.close()
        list2.pop()

class Font:
    def __init__(self):
        self.name = ''

    def getStyle(self):
        return ''

class FontTableDestination(Destination):
    def __init__(self,foutput,parser):
        Destination.__init__(self,foutput,parser)
        self.fontTable = []
        self.name = 'FontTable'

    def getFont(self,index):
        return self.fontTable[index]
    
    def putChar(self,str2):
        font = self.fontTable[-1]
        font.name = font.name + str2

    def doControl(self,token,arg):
        if token == 'f':
            self.fontTable.append(Font())
        elif  token in ['fnil','froman','fswiss','fmodern','fscript','fdecor','ftech','fbidi']:
            self.fontTable[-1].family = token
        elif token == 'fcharset':
            self.fontTable[-1].charset = arg
        else:
            font = self.fontTable[-1]
            setattr(font,token,arg)

class Color:
    def __init__(self):
        self.red = 0
        self.green = 0
        self.blue = 0

    def __str__(self):
        r = hex(self.red)[2:]
        if len(r) == 1:
            r = '0' + r 
        g = hex(self.green)[2:]
        if len(g) == 1:
            g = '0' + g
        b = hex(self.blue)[2:]
        if len(b) == 1:
            b = '0' + b
        return '#%s%s%s' % (r,g,b)

    def __repr__(self):
        return '%i %i %i' % (self.red,self.green,self.blue)

class ColorTableDestination(Destination):
    def __init__(self,foutput,parser):
        Destination.__init__(self,foutput,parser)
        self.name = 'ColorTable'
        self.colorTable = []

    def getColor(self,index):
        return self.colorTable[index]
    
    def putChar(self,str2):
        if str2 == ';':
            self.colorTable.append(Color())

    def doControl(self,token,arg):
        if len(self.colorTable) == 0:
            self.colorTable.append(Color())
        color = self.colorTable[-1]
        setattr(color,token,int(arg))
                
class Rtf2Txt(RtfParser.RtfParser):
    def __init__(self,foutput):
        RtfParser.RtfParser.__init__(self)
        self.foutput = foutput
        self.destinations = [RtfDestination(foutput,self)]
        self._ansicpg = 'latin_1'

    def setAnsiCpg(self,codePage):
        self._ansicpg = codePage or self._ansicpg

    def getAnsiCpg(self):
        try:
            return "cp%d" % int(self._ansicpg)
        except:
            return self._ansicpg

    ansicpg = property(getAnsiCpg,setAnsiCpg,doc='the code page used')

    def getChar(self,code):
        return chr(code)
        #return str(chr(code),self.ansicpg)

    def append(self,arg):
        self.destinations.append(arg)

    def pop(self):
        return self.destinations.pop()

    def setDest(self,dest):
        self.destinations[-1] = dest
        self.ansicpg = dest.ansicpg

    def pushState(self):
        dest = self.destinations[-1]
        dest.pushState(self)
        self.ansicpg = dest.ansicpg

    def popState(self):
        #try:
            dest = self.destinations[-1]
            dest.popState(self)
        #except:
        #    _

    def putChar(self,ch):
        dest = self.destinations[-1]
        if not (ch=='\n' or ch=='\r'):
            dest.putChar(ch)

    def doControl(self,token,arg):
        dest = self.destinations[-1]
        dest.doControl(token,arg)

    def close(self):
        for dest in self.destinations:
            dest.close()


def getTxt(rtf):
    """ get the Text from a string that contain Rtf """
    import io
    s = io.StringIO()
    #try:
    parser = Rtf2Txt(s)
    parser.feed(rtf)
    parser.close()
    #except:
        #return s.getvalue()
    text = s.getvalue().replace('·','· ')  
    return text
