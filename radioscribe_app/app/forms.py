from flask.ext.wtf import Form
from wtforms import StringField, BooleanField
from wtforms.validators import DataRequired
#from flask.ext.wtf import Form
#from wtforms.fields import TextField, BooleanField
#from wtforms.validators import Required

class SearchForm(Form):
    search = StringField('search', validators=[DataRequired()])


class LoginForm(Form):
    search = StringField('search', validators=[DataRequired()])
    
