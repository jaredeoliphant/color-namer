from flask import Flask, render_template, request, Response, session, redirect, flash, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FloatField, FileField, MultipleFileField, BooleanField, IntegerRangeField
from wtforms.validators import Length, DataRequired, NumberRange
# from wtforms.fields.html5 import DecimalRangeField
from werkzeug.utils import secure_filename
import os


app = Flask(__name__)

app.config['SECRET_KEY'] = 'secretkey'


class ColorForm(FlaskForm):

    red = IntegerRangeField('Red')
    green = IntegerRangeField('Green')
    blue = IntegerRangeField('Blue')
    submit = SubmitField('Submit')


@app.route('/', methods=['GET', 'POST'])
def index():
    form = ColorForm()

    if form.validate_on_submit():
        session['red'] = form.red.data
        session['green'] = form.green.data
        session['blue'] = form.blue.data

        return render_template('result.html')

    return render_template('index.html', form=form)


if __name__ == '__main__':
    app.run(debug=True)
    