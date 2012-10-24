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

#[0x22,'*',*,*,*,*,*,*]:[*,*,*,*,*,*,*,*]

# '*' represents wild card

# injects data into bushido brake packet which is then transmitted to headunit 
receive_injections = [

    #([0x22,'*','*','*','*','*','*','*'],['*','*','*','*','*','*','*','*']),
    #([0xdc],['*','*','3','4','5','6','*','8']),
    (['*'],['*',2,3,65,5,6,8,10]),
    #([0x02],['*',0x01,0x2c,65,0,'*','*','*']),
    #([0x01],['*',0x02,0x58,0x01,0x2c,0x01,0x2c,'*']),
    #([0x10],['*','*','*','*','*','*','*','*']),
    #([0x22],['*',2,3,4,5,6,7,8]),
    #([0x22],['*','2','3','4','5','6','7','8']),
    #([0x04],['*',2,3,4,5,6,7,8]),
    #([0x08],['*',2,3,4,5,6,7,8]),
    ([0x10],['*',2,3,4,5,6,7,8]),
    #([0x02],['*',0x02,0x03,0x04,0x05,0x06,0x07,0x08]),
    #([0x22],['*',2,3,4,5,6,7,8]),
    ([0x02],['*',0x04,0xff,0x04,0x05,0x06,0x07,0x08]),
    ([0x01],['*',0x02,0x58,0x00,0x00,0x01,0x2c,'*']),
    
    ([0x22],['*',255,255,255,255,255,255,255]),
    #([0xad],['*',255,255,255,255,255,255,255]),
    ([0x04],['*',255,255,255,255,255,255,255]),
    ([0x08],['*',255,255,255,255,255,255,255]),
    #([0x10],['*',255,255,255,255,255,255,255]),
    ([0xad,0x02,'*','*','*','*','*','*'],['*','*','*',4,'*','*',255,255]),
    #([0xad,0x01],['*','*',255,255,255,255,255,255]),
]

# injects data into packets from headunit destined for brake
transmit_injections = [

    #([0xdc,'*','*','*','*','*','*','*'],[1,'*','*','*','*','*','*','*']),
    #([0x01],['*',1,220,'*','*','*','*','*']),

]