from flask import Flask, render_template, request, Response, session, redirect, flash, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FloatField, FileField, MultipleFileField, BooleanField, IntegerRangeField
from wtforms.validators import Length, DataRequired, NumberRange
# from wtforms.fields.html5 import DecimalRangeField
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


def rgb_to_hex(r, g, b):
    return '#{:X}{:X}{:X}'.format(r, g, b)


class ColorForm(FlaskForm):

    red = IntegerRangeField('Red',default=127)
    green = IntegerRangeField('Green',default=127)
    blue = IntegerRangeField('Blue',default=127)
    submit = SubmitField('Submit')


@app.route('/', methods=['GET', 'POST'])
def index():
    form = ColorForm()

    if form.validate_on_submit():
        session['red'] = form.red.data
        session['green'] = form.green.data
        session['blue'] = form.blue.data
        colornames, hexs, distances = three_closest(form.red.data,form.green.data,form.blue.data)
        session['colorlist'] = ['My Color']+colornames.tolist()
        session['hexlist'] = [rgb_to_hex(form.red.data,form.green.data,form.blue.data)]+hexs.tolist()
        session['distancelist'] = [0.0] + distances.tolist()
        session['howmany'] = 38

        return render_template('result.html')

    return render_template('index.html', form=form)


if __name__ == '__main__':
    app.run(debug=True)
    