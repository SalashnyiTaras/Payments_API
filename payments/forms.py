from flask_wtf import FlaskForm
from wtforms import IntegerField, StringField, SelectField, SubmitField, TextAreaField, FloatField


class PaymentsForm(FlaskForm):
    # TODO: to add field validators
    amount = StringField(label="Amount to pay: ")
    currency = SelectField(label="Choose your currency", choices=[(840, "USD"), (643, "Russian RUB"), (978, "EUR")],
                           coerce=int)
    description = TextAreaField(label="Payment description")
    submit = SubmitField(label="Pay")
