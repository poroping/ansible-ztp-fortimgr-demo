from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, BooleanField
from wtforms.validators import InputRequired

class AddDeviceForm(FlaskForm):
    serial = StringField('Device Serial', validators=[InputRequired()])
    customer = SelectField('Customer', default='', validators=[InputRequired()],
        choices=[('','---'), ('FISH', 'FISH'), ('etc.', 'etc.')])
    line = StringField('Line number', validators=[InputRequired()])
    submit = SubmitField('Add Device')
