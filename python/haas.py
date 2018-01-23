# -*- coding: utf-8 -*-

import sys, math, re
import copy
import classes

'''
различают два состояния: 
    + "текущее" -- в котором находится станок в данный момент времени
    + "целевое" -- заданое в кадре, куда должны переместиться органы станка

грамматикa g-кода: 
 1) "кадр" состоит из "слов"
 2) "слово" формируется как "адрес (буква)" + "цифра (целая или дробная)"
 3) "слова" делятся на типы:
    + координаты (xyzabcuvw): 
        ++ надо хранить два значения Р1 и Р2, т.к. по их разнице определяется вектор движения
        ++ если Р2 в кадре не указан, то остаемся в прежней точке Р1, т.е. координата не изменяется
        ++ после отработки перемещений в конце кадра, при работе в абсолютной системе координат: Р1 = Р2, при работе в приращениях: Р1 += Р2
        ++ имеют различные размерности (мм, дюймы, градусы, радианы)
    + параметры инструмента и шпинделя (tsfdh):
        ++ при включении станка либо остаются занчения от предыдущего включения (например, номер текущего инструмента и корректоры), либо равно 0 (например, частота вращения шпинделя)
        ++ вед себя аналогично координатам: если в кадре значение не указано, то остается предыдущее либо значение обновляется
        ++ контроль ошибок: несоответствие номера корректора и номера инструмента
    + параметры функций (ijkrclpq):
        ++ в различных функциях играют различное назначение (например R: для круговой интерполяции -- это радиус, для цикла сверления -- это высоат плоскости безопасности)
        ++ обнуляются перед выполнением каждого кадра -- их значение принимается "None"
        ++ если в функции неуказан какой-то параметр -- должно вызываться исключение и сообщение о ошибке
    + подготовительные функции(g):
        ++ разбиты по группам: модальных и немодальных (в пределах одной группы может быть включена только одна функция)
        ++ для анализа ошибок модальности надо различать два состояния и накапливать все указанные в кадре g-функции
    + функции управления станком (m):
        ++ полная аналогия g-функциям
        
state0  state1          recalculate state1
 G0      None        ==> G0 (modal)
 G0      G1          ==> G1
 G0      G1 & G2     ==> error (function one group in one block)
 G0      G123        ==> error (incorrect parameters)
 None    R           ==> only for functions parameters
 
 class block()
    state0 = dict('a..z')       # update only
    state1 = dict('a..z')       # in each iteration of g-code lines: reset
    const = g-function by group константы групп g/m функций
    def:
        default -- set default values of state0 --> to _init_
        clear   -- state1[key]=None очистка всех параметров перед началом выполнения кадра --> to _copy_
        set     -- state1[key]=Value установка значений текущего кадра
        recalculate -- state1[key]=state0[key] пересчет модальных значений (логика g-кода)
        copy        -- state0[key]=state1[key] копирования текущего положения после окончания кадра (функция copy object)
'''

def preprocessing(code):
    
# ==== поиск ошибок
    '''
    if len(code) == 0:
        return False, u'Пустой файл'
    
    # Программа должна начинаться и заканчиваться символом "%"
    if len(re.findall(r'\%', code)) != 2:
        return False, u'Программа должна начинаться и заканчиваться символом "%"'

    # Поиск недопустимых символов
    symbols = re.compile('[^A-Z\d\s\.\,\-\:\;\\\+\%\$\(\)]', re.IGNORECASE)
    result = symbols.findall(code)
    if result:
        return False, u'Недопустимые символы: "%s"' % ' '.join(result)
    '''
# ==== первичная обработка текста
    # В качестве УП далее рассматриваем кусок текста между %... %
    # split возвращает список вида: "" % "текст" % "все что дальше - не рассматриваем"
    #code = code.split('%')[1]

    # Удаляем из исходной строки все комментарии (все, что между парными скобками "(...)" )
    code = re.sub('(\(.*\))', '', code)
    
    # Удаляем пустые строки
    code = re.sub('\n\s*\n', '\n', code)    # т.к. весь исходный код - одна строка, то и ищем пробельные символы между двумя \n
    code = re.sub('^\n|\n$', '', code)      # первый и последний символ \n в строке

    # Преобразование всех символов к нижнему регистру
    code = code.lower()

    # разделяем исходную строку на массив строк
    code = code.split("\n")
    
    return True, code


# ===========================================================================================


def processing(gcode):
    
    # compile template for parsing of G-code frame: "any letter" + "real / integer"
    pattern = re.compile('([A-Z])([-+]?[0-9]*\.?[0-9]+)', re.IGNORECASE)
    
    # list to send to browser
    CLData = []
    
    # create current state obj with default values
    s0 = classes.state()
    s0.default()
    
    # analyze each blocks separately
    for line in gcode:
        #print ""
        #print line
        # create target state obj -- planned in block
        s1 = classes.state()

        # search "words"
        words = pattern.findall(line)

        # analyze each "word"
        for word in words:
            name = word[0]             # function name
            number = float(word[1])    # function number or coordinate or feed value ... (convert str-to-float)
            
            # set values in current block
            s1.set(name, number)
        
        # checking for motion in the block (only before update state #1 !!!)
        move = s1.is_move()
        
        # TODO: rewrite to class function!!!
        for key, value in s1.get().iteritems():
            # update state #1 by modal function from state #0
            if (value == None) and (s1.is_modal(key)) and (not s1.is_position(key)):
                setattr(s1, key, getattr(s0,key))
            # set s0 position if absolute distance mode
            if (value == None) and (s1.is_position(key)) and (s1.g3 == 90):
                setattr(s1, key, getattr(s0,key))
            # set 0 if incremental distance mode (to avoid accumulation of unspecified coordinates)
            if (value == None) and (s1.is_position(key)) and (s1.g3 == 91):
                setattr(s1, key, 0)

        #print "move",move
        #print s1
        # generate toolpath (if there is movement in block)
        if move:
            CLData += toolpath(s0, s1)

        # set s1 as current state (s1 will be removed after end of loop)
        for key in s1.get().keys():
            setattr(s0, key, getattr(s1,key))
    
    #print CLData
    return CLData


# ===========================================================================================


def toolpath(s0, s1):
    # первая (начальная) точка траетории, в данном случае -- значение по умолчанию 0,0,0 при создании объекта р0
    block = [[s0.x, s0.y, s0.z, s0.f, s0.s]]

    if s1.g3 == 90:
        if s1.x == None:
            s1.x = s0.x
        if s1.y == None:
            s1.y = s0.y
        if s1.z == None:
            s1.z = s0.z
    # если координаты заданы в приращениях, то преобразовываем их к абсолютным (для отрисовки)
    if s1.g3 == 91:
        s1.x = s0.x if s1.x == None else (s1.x + s0.x)
        s1.y = s0.y if s1.y == None else (s1.y + s0.y)
        s1.z = s0.z if s1.z == None else (s1.z + s0.z)

    # быстрые перемещения
    if s1.g1 == 0:
        s1.f = 10000
        block.append([s1.x, s1.y, s1.z, s1.f, s1.s])

    # линейная интерполяция
    if s1.g1 == 1:
        block.append([s1.x, s1.y, s1.z, s1.f, s1.s])


    # круговая интерполяция
    if s1.g1 == 2: direction = False
    if s1.g1 == 3: direction = True
    if (s1.g1 == 2) or (s1.g1 == 3):
        if s1.g2 == 17:
            if (s1.i == None) and (s1.j != None): 
                s1.i = 0
            elif (s1.i != None) and (s1.j == None):
                s1.j = 0
            elif (s1.i == None) and (s1.j == None):
                print 'Error'
                
            # IF I-J-K
            s1.xc = s0.x + s1.i
            s1.yc = s0.y + s1.j
            # TODO:  IF R....
            
            da0 = s1.xc
            db0 = s1.yc
            da1 = s0.x - s1.xc
            db1 = s0.y - s1.yc
            da2 = s1.x - s1.xc
            db2 = s1.y - s1.yc
        
        # TODO: YZ XZ plane
        
        if direction:
            # изначально в формулах поворот против часовой стрелки
            arc = math.atan2(db2, da2) - math.atan2(db1, da1)
        else:
            # если поворот по часовой стрелке, то:
            arc = math.atan2(db1, da1) - math.atan2(db2, da2)
        # atan2 выдает значения от [-pi...pi], тут приводим к диапазону [0...2pi]
        if arc > math.pi:
            arc = 2 * math.pi - arc
        fi = 0.2
        
        # full circle
        # https://studopedia.ru/3_198520_programmirovanie-interpolyatsii.html
        #if (s1.i == 0) or (s1.j == 0):
        #    arc = 2 * math.pi
            
        step = int(round(arc / fi))
        
        # изначально в формулах поворот против часовой стрелки
        # если поворот по часовой стрелке, то:
        if not direction: fi *= -1
        
        for i in range(step):
            cs = math.cos(fi * i)
            sn = math.sin(fi * i)
            a = da1 * cs - db1 * sn + da0
            b = da1 * sn + db1 * cs + db0
            if s1.g2 == 17: block.append([a, b, s1.z, s1.f, s1.s])
            if s1.g2 == 18: block.append([a, s1.y, b, s1.f, s1.s])
            if s1.g2 == 19: block.append([s1.x, a, b, s1.f, s1.s])
        
        block.append([s1.x, s1.y, s1.z, s1.f, s1.s])
    
    return block

