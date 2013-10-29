from flask import Flask, render_template, request, make_response, abort
from flask_wtf.csrf import CsrfProtect
from flask_mail import Mail, Message
from wtforms.widgets import HTMLString
from forms import ShortMessageForm
from utils import compose_pdf
from linkedin import linkedin
from linkedin.exceptions import BaseLinkedInError
import os


app = Flask(__name__)

if 'PERSONAL_APP_SETTINGS' in os.environ:
    app.config.from_envvar('PERSONAL_APP_SETTINGS')

CsrfProtect().init_app(app)
mail = Mail()
mail.init_app(app)


@app.route('/')
def index():
    authentication = linkedin.LinkedInDeveloperAuthentication(
        app.config['LINKEDIN_API_KEY'],
        app.config['LINKEDIN_API_SECRET'],
        app.config['LINKEDIN_USER_TOKEN'],
        app.config['LINKEDIN_USER_SECRET'],
        request.base_url,
        linkedin.PERMISSIONS.enums.values())
    application = linkedin.LinkedInApplication(authentication)
    try:
        profile = application.get_profile(selectors=[
            'id',
            # general info
            'first-name',
            'last-name',
            'headline',
            'summary',
            # contact info
            'email-address',
            'phone-numbers',
            'public-profile-url',
            # profile
            'location',
            'positions',
            'skills',
            'educations',
        ])
        # profile picture
        profile['pictureUrls'] = application.get_picture_urls()
    except BaseLinkedInError as e:
        profile = None
        app.logger.warning('Caught an exception while trying to get the linkedin profile: %s' % e)
    form = ShortMessageForm()
    return render_template('index.html', profile=profile, form=form)


@app.route('/send_message', methods=['POST'])
def message():
    if request.is_xhr:
        form = ShortMessageForm()
        if not form.validate():
            return render_template('short_message_form.html', form=form)
        # send an email if the form is valid
        msg = Message("I've just sent you a message from your personal site", sender=form.email.data, recipients=[app.config['EMAIL']])
        msg.body = form.message.data
        mail.send(msg)
        return HTMLString("<div class='alert alert-success'>Thank you for the feedback. I will try to reply as soon as possible.</div>")
    abort(404)


@app.route('/get_pdf')
def pdf():
    pdf = compose_pdf()
    response = make_response(pdf)
    response.headers['Content-Disposition'] = "attachment; filename='test.pdf'"
    response.mimetype = 'application/pdf'
    return response


@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404


if __name__ == '__main__':
    app.run(host=app.config['HOST'])
