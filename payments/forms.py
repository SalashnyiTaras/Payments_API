from flask_wtf import FlaskForm
from wtforms import SelectField, SubmitField, FloatField, StringField
from wtforms.validators import Length, DataRequired, NumberRange


class PaymentsForm(FlaskForm):

    amount = FloatField(label="Amount to pay:",
                        validators=[NumberRange(1, 5000), DataRequired()])
    currency = SelectField(label="Choose your currency",
                           choices=[(978, "EUR"), (840, "USD"), (643, "RUB")], coerce=int)
    description = StringField(label="Payment description", validators=[Length(min=15, max=100,
                              message='Description must be between 15 and 100 characters long.'), DataRequired()])
    submit = SubmitField(label="Pay")
