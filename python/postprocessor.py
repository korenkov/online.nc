# -*- coding: utf-8 -*-

import sys, math, re, os

g_groups = {'group0': [4, 10, 28, 30, 53, 92, 92.1, 92.2, 92.3],
            'group1': [0, 1, 2, 3, 33, 38, 73, 76, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89],
            'group2': [17, 18, 19],
            'group3': [90, 91]
            }

def SetRegister(name, number, register):
    if name in ['x','y','z']:
        register['%s1' % name] = number
    if name in ['i','j','k']:
        register[name] = number
        # функция G02/G03 может быть определена через IJK или R
        # в кадре может быть запись R, а в регистре сохранены IJK из предыдущих кадров
        # в результате будет неопределенность, какое значение принимать, поэтому
        # параметром 'circle_mode' определяется режим задания дуги в текущем кадре
        # (предполагается, что одновременно G02/G03 I J K R в одном кадре встречаться не могут)
        register['circle_mode'] = 'ijk'
    if name in ['r']:
        register[name] = number
        register['circle_mode'] = 'r'
    if name in ['t','s','f']:
        register[name] = number
    if name == 'g':
        for key, value in g_groups.items():
            if number in value:
                register[key] = number



def angle_between_vectors(a0,b0,a1,b1,a2,b2, direction):
    # изначально в формулах поворот против часовой стрелки
    if direction:
        da1 = a1 - a0
        db1 = b1 - b0
        da2 = a2 - a0
        db2 = b2 - b0
    else:    
    # если поворот по часовой стрелке, то:
        da2 = a1 - a0
        db2 = b1 - b0
        da1 = a2 - a0
        db1 = b2 - b0
    a = math.atan2(da1*db2-da2*db1, da1*da2+db1*db2)
    # atan2 выдает значения от [-pi...pi], тут приводим к диапазону [0...2pi]
    if a < 0:
        a = 2*math.pi + a
    return a
    
def rotation_vector(a0,b0,a1,b1,fi, direction):
    # изначально в формулах поворот против часовой стрелки
    # если поворот по часовой стрелке, то:
    if not direction:
        fi *= -1
    cs = math.cos(fi)
    sn = math.sin(fi)
    a = (a1 - a0) * cs - (b1 - b0) * sn + a0
    b = (a1 - a0) * sn + (b1 - b0) * cs + b0
    return a,b




def ToolPathCalculation(register):
    block = []
    
    if register['group3'] == 91:
        register['x1'] += register['x0']
        register['y1'] += register['y0']
        register['z1'] += register['z0']
    
    if register['group1'] == 0:
        register['f'] = 1000
        block.append([register['x1'], register['y1'], register['z1'], register['f'], register['s']])
        
    if register['group1'] == 1:
        block.append([register['x1'], register['y1'], register['z1'], register['f'], register['s']])

    '''
    if (register['group1'] == 2) or (register['group1'] == 3):
        if register['circle_mode'] == 'ijk' and register['group2'] == 17:
            register['r'] = math.sqrt(register['i']*register['i'] + register['j']*register['j'])
        if register['circle_mode'] == 'ijk' and register['group2'] == 18:
            register['r'] = math.sqrt(register['i']*register['i'] + register['k']*register['k'])
        if register['circle_mode'] == 'ijk' and register['group2'] == 19:
            register['r'] = math.sqrt(register['j']*register['j'] + register['k']*register['k'])
    '''
    if register['group1'] == 3:
        xc = register['x0'] + register['i']
        yc = register['y0'] + register['j']
        register['r'] = math.sqrt(register['i']*register['i'] + register['j']*register['j'])
        # angle_between_vectors
        arc = angle_between_vectors(xc,yc,register['x0'],register['y0'],register['x1'],register['y1'], True)
        fi = 0.2 #1/register['r']
        step = int(round(arc / fi))
        print "begin = ", register['x0'], register['y0'], "  end = ", register['x1'], register['y1'], "  center = ", xc, yc, "  arc = ", math.degrees(arc)
        print "step = ", step, " R = ", register['r']
        
        for i in range(step):
            x,y = rotation_vector(xc, yc, register['x0'], register['y0'], fi * i, True)
            block.append([x,y, register['z1'], register['f'], register['s']])
        block.append([register['x1'], register['y1'], register['z1'], register['f'], register['s']])


    if register['group1'] == 2:
        xc = register['x0'] + register['i']
        yc = register['y0'] + register['j']
        register['r'] = math.sqrt(register['i']*register['i'] + register['j']*register['j'])
        # angle_between_vectors
        arc = angle_between_vectors(xc,yc,register['x0'],register['y0'],register['x1'],register['y1'], False)
        fi = 0.2 #5/register['r']
        step = int(round(arc / fi))
        print "begin = ", register['x0'], register['y0'], "  end = ", register['x1'], register['y1'], "  center = ", xc, yc, "  arc = ", math.degrees(arc)
        print "step = ", step, " R = ", register['r']
        for i in range(step):
            x,y = rotation_vector(xc, yc, register['x0'], register['y0'], fi * i, False)
            block.append([x,y, register['z1'], register['f'], register['s']])
        block.append([register['x1'], register['y1'], register['z1'], register['f'], register['s']])
            

    return block


'''
def angle_between_vectors(x0,y0,x1,y1,x2,y2):
    dx1 = x1 - x0
    dy1 = y1 - y0
    dx2 = x2 - x0
    dy2 = y2 - y0
    a = math.atan2(dx1*dy2-dx2*dy1, dx1*dx2+dy1*dy2)
    if a < 0:
        a = 2*math.pi + a
    return a

def rotation_vector(x0,y0,x1,y1,a):
    cs = math.cos(a)
    sn = math.sin(a)
    x = (x1 - x0) * cs - (y1 - y0) * sn + x0
    y = (x1 - x0) * sn + (y1 - y0) * cs + y0
    return x,y

fi = math.radians(-13)
x0 = 2
y0 = 1
x1 = 1
y1 = 7
x2, y2 = rotation_vector(x0,y0,x1,y1,fi)

print (round(math.degrees(angle_between_vectors(x0,y0,x1,y1,x2,y2) ),1))

'''
