'''
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

Created on 8 Dec 2016

@author: elyne
'''
from DeIdColl import DeIdentifier
from DeIdColl import DeIdentifyCategories
from DeIdColl import importDEIDresources


if __name__ == '__main__':
    
    text = '''
    Geachte collega,
    
    Ik mail u in verband met Piet Van De Borre.
    
    Hij is namelijk ziek.
    
    Met Vriendelijke Groeten,
    Dr. Frank Verlinden'''
    
    summary = "doodziek"
    
    gazet = importDEIDresources.getGazetteers()
    deid = DeIdentifier.DeIdentifier(text, gazet)
    print(deid.deidentifyRAW(1))
    
    ##sum2 = an optional summary of the document
    print(DeIdentifyCategories.processProtocol(text, summary))
    
    print(DeIdentifyCategories.processOK(text, summary))
    
    print(DeIdentifyCategories.processBrief(text, summary))