#    
#    Copyright (c) 2012, Will Szumski
#    Copyright (c) 2012, Doug Szumski
#
#    This file is part of PyBushido.
#
#    PyBushido is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    Foobar is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with PyBushido.  If not, see <http://www.gnu.org/licenses/>.
#
#

import injections
from bushido import partial_compare_list

def compare(data,template):
    data = list(data)
    for index, value in enumerate(template):
        if value == '*':
            data[index] = value
    return partial_compare_list(template,data)
    
    
def injectReceive(data):
    reload(injections)
    for matcher,replacements in injections.receive_injections:
        injectOnMatch(data,matcher,replacements)
        
def injectTransmit(data):
    reload(injections)
    for matcher,replacements in injections.transmit_injections:
        injectOnMatch(data,matcher,replacements)

def injectOnMatch(data, matcher,replacements):
    if compare(data,matcher):
        for index,value in enumerate(replacements):
            if value != '*':
                data[index] = value
    return data    
    
if __name__ == '__main__':
    test = [0xdc, 0x02, 0x00, 0x99, 0x00, 0x00, 0x00, 0x00]
    print test
    injectReceive(test)
    print test
    test = [0xdc, 0x02, 0x00, 0x99, 0x00, 0x00, 0x00, 0x00]
    print test
    injectTransmit(test)
    print test