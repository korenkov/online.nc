#!/usr/bin/python
# -*- coding: utf-8 -*-

import os, re

group = {}
group['non_modal'] 			= ['G4', 'G10', 'G28', 'G30', 'G53', 'G92', 'G92.1', 'G92.2', 'G92.3']
group['motion'] 			= ['G0', 'G1', 'G2', 'G3', 'G38.2', 'G80', 'G81', 'G82', 'G84', 'G85', 'G86', 'G87', 'G88', 'G89']
group['plane_selection']	= ['G17', 'G18', 'G19'] 
group['distance_mode'] 		= ['G90', 'G91'] 
group['feed_rate_mode'] 	= ['G94', 'G95']
group['units'] 				= ['G20', 'G21'] 
group['radius_compensation']= ['G40', 'G41', 'G42']
group['tool_length_offset']	= ['G43', 'G49'] 
group['canned_cycles_mode']	= ['G98', 'G99']
group['coordinate_system'] 	= ['G54', 'G55', 'G56', 'G57', 'G58', 'G59', 'G59.3']
group['path_control_mode'] 	= ['G61', 'G61.1', 'G64']
group['stopping']			= ['M0', 'M1', 'M2', 'M30', 'M60'] 
group['axis_clamping']		= ['M26', 'M27'] 
group['tool_change']		= ['M6'] 
group['spindle_turning']	= ['M3', 'M4', 'M5'] 
group['coolant']			= ['M7', 'M8', 'M9']
group['override_controls']	= ['M48', 'M49']
group['tool_number']		= ['T%s' % i for i in range(1,13)]


buffer = { x:None for x in 'ABCDEFHIJKLNOPQRSUVWXYZ' }
buffer.update( { key:None for key,value in group.iteritems() } )


# Функция для определения шаблона "буква" + "число"
def parseWord(word, pattern):
	a = b = None
	result = pattern.findall(word)
	if result:
		a = result[0][0]	
		b = result[0][1]
	# если число отсутсвует (буква должна быть всегда) или результат
	# парсинга не соответсвует исходной строке (написание отличается от заданной маски)
	if not b or (a+b != word): return False, a, b	
	return True, a, b	
	

def CheckError(lines):
	symbols = re.compile('[^A-Z\d\s\.\-\+\%\(\)]', re.IGNORECASE)
	comments = re.compile('(\(.*\))', re.IGNORECASE)
	bracket = re.compile('[\(\)]{1}', re.IGNORECASE)
	empty_line = re.compile('^\s*$')
	space = re.compile('([^\s])([A-Z])', re.IGNORECASE)
	
	f1 = re.compile('([^\W\dGTM]){1}([+-]?\d{,5}\.?\d{,3})', re.IGNORECASE)	
	f2 = re.compile('([G]){1}(\d{1,3}\.?\d?)', re.IGNORECASE)			
	f3 = re.compile('([MT]){1}(\d{1,2})', re.IGNORECASE)				
	f4 = re.compile('([O]){1}(\d{4,5})', re.IGNORECASE)				
	
	# УП должна начинаться с знака % (строка №1)
	if lines[0] != '%': return True, 1, 'Программа должна начинаться и заканчиваться символом "%"'
	# Находим закрывающий символ %
	n = len(lines)
	for i in range(1,n):		
		if lines[i] == '%': break
	if (i == n-1) and (lines[n-1] != '%'): return True, n, 'Программа должна начинаться и заканчиваться символом "%"'

	# В качестве УП далее рассматриваем кусок текста между %... %
	lines = lines[1:i]
	
	# Счетчик строки, в которой будет найдена ошибка
	line_number = 1
	for text in lines:
		line_number += 1
		
		# 1. Пропускаем пустые строки
		if empty_line.findall(text): continue
		# 2. Поиск недопустимых символов
		result = symbols.findall(text)
		if result: return True, line_number, 'Недопустимый символ: "%s"' % (' ; '.join(result)).encode('utf-8')
		# 3. Удаляем из исходной строки все комментарии (все, что между парными скобками "(...)" )
		text = re.sub(comments, '', text)
		# 4. Поиск НЕзакрытых скобок комментарием
		if bracket.findall(text): return True, line_number, 'Незакрытая скобка'
	
		# добавляем пробелы перед каждой буквой -- для определения функций, написанных слитно
		text = re.sub(space, r'\1 \2', text)
		# удаляем поворяющиеся пробелы (юникодные в том числе) и пропуски на концах строки
		text = re.sub('(?u)\s+', r' ', text).strip()
		# для дальнейшего анализа принимаем список слов начинающихся с буквы
		result = re.split('\s+', text)
	
		for word in result:
			print '--', f4.findall(word)
			print '==',[value for key,value in buffer.iteritems() ]
			# В названии после буквы "О" должно идти 4-5 цифр
			if re.compile('O.*', re.IGNORECASE).findall(word):
				if (len([value for key,value in buffer.iteritems() if value != None ]) !=0 ) or not f4.findall(word): return True, line_number, 'Ошибка в названии программы'
			state,f,v = parseWord(word,f4)
			if state:
				buffer[ f.upper() ] = v
				continue
			# ищем переменные
			state,f,v = parseWord(word,f1)
			if state:
				buffer[ f.upper() ] = float(v)
				continue
			# ищем функции G
			state,f,v = parseWord(word,f2)
			if state:
				pass
			# ищем функции М и Т
			state,f,v = parseWord(word,f3)
			if state:
				pass
			return True, line_number, 'Ошибка в выражении: "%s"' % (word).encode('utf-8')

	

	return False, line_number, 'G-code has no errors!'
