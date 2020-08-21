from flask_wtf import Form
from wtforms.fields.html5 import DateField

class SubmitDownload(Form):
    dt = DateField('DatePicker', format='%Y-%m-%d')

