# -*- coding: utf-8 -*-

import sys, math, re

class state(object):
    # groups of G-function (for example: g2 is not circular interpolation), group #2 "plane selection": G17 or G18 or G19 function
    __ggroups = {   u'g0':  [4, 10, 28, 30, 53, 92, 92.1, 92.2, 92.3],    # non modal
                    u'g1':  [0, 1, 2, 3, 33, 38, 73, 76, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89], # motion
                    u'g2':  [17, 18, 19],       # plane selection
                    u'g3':  [90, 91],           # distance mode
                    u'g4':  [20, 21],           # units
                    u'g5':  [93, 94],           # feed rate mode
                    u'g7':  [40,41,42],         # cutter radius compensation
                    u'g8':  [43, 49],           # length offset
                    u'g10': [98, 99],           # return mode in canned cycles
                    u'g12': [54,55,56,57,58,58],# coordinate system selection
                    u'g13': [61, 62.1, 64],     # path control mode
                }
                
    # groups of M-function (constant)            
    __mgroups = {   u'm0':  [0, 5, 30],
                    u'm1':  [28],
                }

    # alphabet (constant):
    __position = ['x','y','z','a','b','c']                      # position (address of linear & rotary axis)
    __tool = ['t','f','s','h','d']                              # tool & spindel address
    __parameters = ['xc','yc','zc','i','j','k','r','l','q','n']   # parameters of G-funtion
    __preparatory = [item for item in __ggroups.keys()]         # groups of G-function 
    __miscellaneous = [item for item in __mgroups.keys()]       # groups of M-function
    
    # get all litearl address
    __slots__ = sum([__position, __tool, __parameters, __preparatory, __miscellaneous], [])

#======================================================================================================
    def __init__(self):
        for item in self.__slots__: setattr( self, item, None )

#======================================================================================================
    def default(self):
        # set default values of G-function
        self.g1 = 80
        self.g2 = 17
        self.g3 = 90
        self.g5 = 94
        self.g7 = 40
        # set default position
        self.x = 0
        self.y = 0
        self.z = 100
        # set default speed & feddrate
        self.s = 0 
        self.f = 0
    
#======================================================================================================
    def is_modal(self, name):
        if (name in self.__parameters) or (name == 'g0'):
            return False
        else:
            return True

#======================================================================================================
    def is_move(self):
        for item in sum([self.__position, self.__parameters], []):
            if getattr(self, item) != None:
                return True
        return False

#======================================================================================================
    def is_position(self, name):
        if (name in self.__position):
            return True
        else:
            return False
        
#======================================================================================================
    def get(self):
        return {item: getattr(self, item) for item in self.__slots__}

#======================================================================================================
    def set(self, key, value):
        if key == 'g':
            for key_group, value_group in self.__ggroups.items():
                if value in value_group:
                    setattr(self, key_group, value)
                # TODO: выполнить проверку на наличие ошибки (в кадре более одной функции в одной группе)
        # TODO:
        elif key == 'm':
            pass
        
        elif key in self.__slots__:
            setattr(self, key, value)
        else:
            #TODO: error --> invalid key
            print "invalid key: %s  for value: %s " % (key, value)

    def __repr__(self):
        return str({key: getattr(self, key) for key in self.__slots__})

