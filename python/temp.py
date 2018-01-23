# -*- coding: utf-8 -*-

import math, re

'''
#x0 = 30
#y0 = 5
x1 = 10
y1 = 10
x2 = 35
y2 = 25

i = 20
j = -5


da0 = i + x1
db0 = j + y1
da2 = x1 - da0
db2 = y1 - db0
da1 = x2 - da0
db1 = y2 - db0

a1 = math.atan2(db1, da1)
#if a1 < 0:
#    a1 += 2* math.pi
        
a2 = math.atan2(db2, da2)
#if a2 < 0:
#    a2 += 2* math.pi

# CW
direction = False

a = a2 - a1
if a > math.pi:
    a = 2 * math.pi - a

print math.degrees(a)

fi = 0.2
step = int(round(a / fi))

if not direction: fi *= -1
for i in range(step):
    cs = math.cos(fi * i)
    sn = math.sin(fi * i)
    a = da1 * cs - db1 * sn + da0
    b = da1 * sn + db1 * cs + db0
    print fi*i,a,b
'''





'''
code = %

( Made using CamBam - www.cambam.co.uk )
G21 G90 G64 G40
G0 Z3.0
( T0  3.175 )
T0 M6
( Roughing русские)
G17
M3 S1000
G0 X2.5548 Y22.4311
G1 F300.0 Z-1.0
G1 F2000.0 X0.5567 Y26.0488
G2 X0.5411 Y26.0931 I0.1247 J0.0689
G1 X-0.1404 Y29.9754
G2 Y30.0246 I0.1404 J0.0246
G1 X0.4558 Y33.4206
%

import haas

state, msg = haas.preprocessing(code)
if not state:
    print "Error!!! ", msg
else:
    code = msg
    print haas.processing(code)
'''
'''
import classes
block = classes.statement()
block.s1.f = 3500
block.s1['s'] = 500
block.s1['g1'] = 2
block.s1.g2 = 19
#print block
'''

class dotdict(object):
    #__slots__ = ('x','y','z','a','b','c')
    
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
    
    __position = ['x','y','z','a','b','c']

    __slots__ = sum([__position], [])

    def __init__(self):
        for i in self.__slots__:
            setattr( self, i, 0 )
        self.z = 100
    
    def get(self):
        return {k: getattr(a, k) for k in a.__slots__}
    
    def __getattribute__(self, name):
        print '==',name
        #return getattr(self, name)
        try:
            return object.__getattribute__(self, name)
        except:
            return "Value of %s" % name
        
a = dotdict()

a.y = 3
a.b = 200
a.c = 50
for i,v in a.get().iteritems():
    if v == 0:
        setattr(a, i, 40)
    
#print a.get()
print a.b, a.y, a.x



#for key in vars(a):
#    print key, a.key
#print {k: getattr(a, k) for k in a.__slots__}
#import classes
#b = classes.state()
#b.x = 100
#b['g'] = 500
#print b
