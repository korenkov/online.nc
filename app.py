# -*- coding: utf-8 -*-

from flask import Flask, render_template, url_for, request, send_from_directory, jsonify, json
import sys, math, re, os

# import from folder "python" module "postprocessor" (in "python" folder mast be empty file "__init__.py")
import python.postprocessor as postprocessor
import python.haas as haas

app = Flask(__name__)

@app.route('/')
def main(name=None):
    return render_template('base.html')

@app.route('/robots.txt')
@app.route('/favicon.ico')
def static_files():
    return send_from_directory(app.static_folder, request.path[1:])	


@app.route('/get_xyz', methods=['POST'])
def get_xyz():

    # получаем данные, разделяем на строки
    data = json.loads(request.data)

    state, msg = haas.preprocessing(data['gcode'])
    if not state:
        print "Ошибка!!! ", msg
    else:
        CLData = haas.processing(msg)
        return jsonify(CLData)



@app.route('/get_parsing_result', methods=['POST'])
def get_parsing_result():
    # описание см.функцию get_xyz
    data = json.loads(request.data)
    gcode = data['gcode'].split("\n")
    pattern = re.compile('([A-Z])([-+]?[0-9]*\.?[0-9]+)', re.IGNORECASE)
    functions = ['num','block','x','y','z','i','j','k','f','s']
    register = { item:0 for item in functions }
    toolpath = []
    for line in gcode:
        register['block'] = line
        register['num'] += 1
        get_functions = pattern.findall(line)
        for fn in get_functions:
            name = fn[0].lower()
            number = fn[1]
            if name in functions:
                register[name] = number
        toolpath.append([register[item] for item in functions])
    return jsonify(toolpath)
    

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5500)

