from flask_wtf import Form
from wtforms import StringField, TextAreaField
from wtforms.validators import Email, Length, DataRequired


class ShortMessageForm(Form):
    """
    Form - send a short message.
    Has two fields - email and message.
    """
    email = StringField("Email", description="So that I could email you back", validators=[DataRequired(message="This field is required."),
        Email(message="This does not look like a valid email address.")])
    message = TextAreaField("Message", description="Maximum 300 characters", validators=[DataRequired(message="This field is required."),
        Length(max=300, message="The message can not be longer than 300 characters.")])
