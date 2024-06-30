from flask_wtf import FlaskForm
from wtforms import SelectField, SubmitField, StringField, DateField, PasswordField, BooleanField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo
from models import User

class ReservationForm(FlaskForm):
    name = StringField('Twoje Imię', validators=[DataRequired()])
    phone = StringField('Numer Telefonu', validators=[DataRequired()])
    service = SelectField('Usługa', choices=[], coerce=int, validators=[DataRequired()])
    date = DateField('Data', format='%Y-%m-%d', validators=[DataRequired()])
    time = SelectField('Godzina', choices=[(f"{h:02d}:00", f"{h:02d}:00") for h in range(8, 17)] + [(f"{h:02d}:30", f"{h:02d}:30") for h in range(8, 16)], validators=[DataRequired()])
    submit = SubmitField('Zarezerwuj')

class LoginForm(FlaskForm):
    username = StringField('Nazwa użytkownika', validators=[DataRequired()])
    password = PasswordField('Hasło', validators=[DataRequired()])
    remember_me = BooleanField('Zapamiętaj mnie')
    submit = SubmitField('Zaloguj się')

class RegistrationForm(FlaskForm):
    username = StringField('Nazwa użytkownika', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Hasło', validators=[DataRequired()])
    password2 = PasswordField(
        'Powtórz hasło', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Zarejestruj się')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Proszę użyć innej nazwy użytkownika.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Proszę użyć innego adresu email.')
