from flask import Flask, render_template, request, Response, session, redirect, flash, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FloatField, FileField, MultipleFileField, BooleanField
from wtforms.validators import Length, DataRequired, NumberRange
# from wtforms.fields.html5 import DecimalRangeField
from wtforms.widgets.html5 import ColorInput#, IntegerRangeField
# from flask.ext.wtf.html5 import ColorInput
from werkzeug.utils import secure_filename
import os
import pandas as pd
import numpy as np

app = Flask(__name__)

app.config['SECRET_KEY'] = 'secretkey'


def three_closest(r,b,g):
    df = pd.read_csv(os.path.join(os.path.dirname(__file__),'static','files','colors.csv'),names=['name','pretty_name','hex','R','G','B'])
    my_color = np.array([r,b,g])
    distance = [np.linalg.norm(my_color - np.array([row.R,row.G,row.B])) for i,row in df.iterrows()]
    df['distance'] = distance
    three = df.sort_values(by='distance').head(50)
    return three.pretty_name, three.hex, three.distance


def three_closest_weighted(r,b,g):
    df = pd.read_csv(os.path.join(os.path.dirname(__file__),'static','files','colors.csv'),names=['name','pretty_name','hex','R','G','B'])
    my_color = np.array([r,b,g])
    distance = [0.3*(my_color[0]-row.R)**2 + 0.59*(my_color[1]-row.G)**2 \
    + 0.11*(my_color[2]-row.B)**2 for i,row in df.iterrows()]
    df['weighted_distance'] = distance
    three = df.sort_values(by='weighted_distance').head(50)
    print(three)
    return three.pretty_name, three.hex, three.weighted_distance


def rgb_to_hex(r, g, b):
    return '#{:X}{:X}{:X}'.format(r, g, b)

def hex_to_rgb(value):
    value = value.lstrip('#')
    lv = len(value)
    return tuple(int(value[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))


class ColorForm(FlaskForm):

    # red = IntegerRangeField('Red',default=127)
    # green = IntegerRangeField('Green',default=127)
    # blue = IntegerRangeField('Blue',default=127)
    background_color = StringField(widget=ColorInput())
    submit = SubmitField('Submit')


@app.route('/', methods=['GET', 'POST'])
def index():
    form = ColorForm()

    if form.validate_on_submit():
        r, g, b = hex_to_rgb(form.background_color.data)
        session['red'] = r
        session['green'] = g
        session['blue'] = b
        colornames, hexs, distances = three_closest(r,g,b)
        w_colornames, w_hexs, w_distances = three_closest_weighted(r,g,b)
        session['colorlist'] = ['My Color']+colornames.tolist()
        session['hexlist'] = [form.background_color.data]+hexs.tolist()
        session['distancelist'] = [0.0] + distances.tolist()
        session['w_colorlist'] = ['My Color']+w_colornames.tolist()
        session['w_hexlist'] = [form.background_color.data]+w_hexs.tolist()
        session['w_distancelist'] = [0.0] + w_distances.tolist()
        session['howmany'] = 10

        return render_template('result.html')

    return render_template('index.html', form=form)



if __name__ == '__main__':
    app.run(debug=True)
