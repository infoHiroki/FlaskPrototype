from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, BooleanField, SubmitField
from wtforms.validators import DataRequired

class VideoForm(FlaskForm):
    """Form for adding or editing a video."""
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Description')
    vimeo_id = StringField('Vimeo ID', validators=[DataRequired()])
    vimeo_hash = StringField('Vimeo Hash')
    is_public = BooleanField('Is Public')
    submit = SubmitField('Save Video')
