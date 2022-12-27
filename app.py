from flask import Flask, render_template, request, session, redirect
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
import os
import pandas as pd
import numpy as np

app = Flask(__name__)

app.config['SECRET_KEY'] = 'secretkey'


def three_closest(r, b, g):
    df = pd.read_csv(os.path.join(os.path.dirname(__file__),
                                  'static', 'files', 'colors.csv'),
                     names=['name', 'pretty_name', 'hex', 'R', 'G', 'B'])
    my_color = np.array([r, b, g])
    distance = [np.linalg.norm(my_color - np.array([row.R, row.G, row.B])) for i, row in df.iterrows()]
    df['distance'] = distance
    three = df.sort_values(by='distance').head(20)
    return three.pretty_name, three.hex, three.distance


def three_closest_weighted(r, b, g):
    df = pd.read_csv(os.path.join(os.path.dirname(__file__),
                                  'static', 'files', 'colors.csv'),
                     names=['name', 'pretty_name', 'hex', 'R', 'G', 'B'])
    my_color = np.array([r, b, g])
    distance = [0.3*(my_color[0]-row.R)**2 + 0.59*(my_color[1]-row.G)**2 +
                0.11*(my_color[2]-row.B)**2 for i, row in df.iterrows()]
    df['weighted_distance'] = distance
    three = df.sort_values(by='weighted_distance').head(20)
    # print(three)
    return three.pretty_name, three.hex, three.weighted_distance


def three_closest_lab(L, A, B):
    df = pd.read_csv(os.path.join(os.path.dirname(__file__),
                                  'static', 'files', 'colors.csv'),
                     names=['name', 'pretty_name', 'hex', 'R', 'G', 'B'])
    my_color = np.array([L, A, B])
    listoftuples = [rgb_to_cielab(row.R, row.G, row.B) for i, row in df.iterrows()]
    # print('in the function')
    # print(listoftuples[4])
    distance = [np.linalg.norm(my_color - np.array([tup[0], tup[1], tup[2]])) for tup in listoftuples]
    df['lab_distance'] = distance
    three = df.sort_values(by='lab_distance').head(20)
    # print(three)
    return three.pretty_name, three.hex, three.lab_distance


def rgb_to_hex(r, g, b):
    return '#{:X}{:X}{:X}'.format(r, g, b)


def hex_to_rgb(value):
    value = value.lstrip('#')
    lv = len(value)
    return tuple(int(value[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))


def rgb_to_cielab(r, g, b):
    # sR, sG and sB(Standard RGB) input range = 0 ÷ 255
    # X, Y and Z output refer to a D65 / 2° standard illuminant.
    rgb = np.array([r, g, b])

    var_rgb = rgb/255

    cons = 0.04045
    for i in range(len(var_rgb)):
        if var_rgb[i] > cons:
            var_rgb[i] = ((var_rgb[i] + 0.055)/1.055)**2.4
        else:
            var_rgb[i] = var_rgb[i] / 12.92

    var_rgb = var_rgb * 100

    X = var_rgb[0] * 0.4124 + var_rgb[1] * 0.3576 + var_rgb[2] * 0.1805
    Y = var_rgb[0] * 0.2126 + var_rgb[1] * 0.7152 + var_rgb[2] * 0.0722
    Z = var_rgb[0] * 0.0193 + var_rgb[1] * 0.1192 + var_rgb[2] * 0.9505

    var_X = np.array([X/95.047,
                      Y/100.000,
                      Z/108.883])

    cons = 0.008856
    for i in range(len(var_X)):
        if var_X[i] > cons:
            var_X[i] = (var_X[i])**(1/3)
        else:
            var_X[i] = 7.787 * var_X[i] + 6/116

    return (116 * var_X[1] - 16,
            500 * (var_X[0] - var_X[1]),
            200 * (var_X[1] - var_X[2]))


class ColorForm(FlaskForm):

    # red = IntegerRangeField('Red',default=127)
    # green = IntegerRangeField('Green',default=127)
    # blue = IntegerRangeField('Blue',default=127)
    # background_color = StringField(widget=ColorInput())
    submit = SubmitField('Submit')


@app.route('/', methods=['GET', 'POST'])
def index():
    form = ColorForm()

    if form.validate_on_submit() and request.method == 'POST':
        # print(request.form.get('color-picker'))
        r, g, b = hex_to_rgb(request.form.get('color-picker'))
        session['red'] = r
        session['green'] = g
        session['blue'] = b

        L, A, B = rgb_to_cielab(r, g, b)

        colornames, hexs, distances = three_closest(r, g, b)
        w_colornames, w_hexs, w_distances = three_closest_weighted(r, g, b)
        lab_colornames, lab_hexs, lab_distances = three_closest_lab(L, A, B)

        session['colorlist'] = ['My Color']+colornames.tolist()
        session['hexlist'] = [request.form.get('color-picker')]+hexs.tolist()
        session['distancelist'] = [0.0] + distances.tolist()

        session['w_colorlist'] = ['My Color']+w_colornames.tolist()
        session['w_hexlist'] = [request.form.get('color-picker')]+w_hexs.tolist()
        session['w_distancelist'] = [0.0] + w_distances.tolist()

        session['lab_colorlist'] = ['My Color'] + lab_colornames.tolist()
        session['lab_hexlist'] = [request.form.get('color-picker')] + lab_hexs.tolist()
        session['lab_distancelist'] = [0.0] + lab_distances.tolist()

        session['howmany'] = 10

        session['thename'] = list(set(colornames.tolist()[:1] + w_colornames.tolist()[:1] + lab_colornames.tolist()[:1]))
        print(session['thename'])
        session['length'] = len(session['thename'])

        return render_template('result.html')

    return render_template('index.html', form=form)


if __name__ == '__main__':
    app.run(debug=True)
