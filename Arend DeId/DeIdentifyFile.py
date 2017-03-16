'''
This script reads a file in the input folder, processes all texts in them, 
and makes a de-identified output file.

The input file used has text in RTF format, with one line per text. Special characters, such as newline, are escaped in those texts.

Copyright (C) 2016 Elyne Scheurwegs, Kim Luyckx

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

Created on 12 Dec 2016

@author: elyne
'''
import config as cfg
import DeIdColl.Rtf2Txt as Rtf2Txt
import DeIdColl.DeIdentifyCategories as DeIdentifyCategories

if __name__ == '__main__':
    cnt = 0
    for line in open(cfg.PATH_IN + 'texts.txt'):
        line = line.replace('\n','')
        
        text = Rtf2Txt.getTxt(line)
        
        text = DeIdentifyCategories.processNota(text,0) 
        
        print(cnt)
        print(text)
        #print(.replace('\n','<newline>'))
        cnt += 1
        
        
    
    
    
    
    
    pass