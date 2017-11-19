import os
from flask import Flask, flash, redirect, render_template, request, make_response, abort, g, url_for
from flask_wtf.csrf import CsrfProtect
from flask_mail import Mail, Message
from werkzeug.local import LocalProxy
from werkzeug.contrib.cache import FileSystemCache
from forms import ShortMessageForm
from utils import compose_pdf
from linkedin import linkedin
from linkedin.exceptions import LinkedInError


app = Flask(__name__)
# Read the config path from the env var if exists.
try:
    app.config.from_envvar('PERSONAL_APP_SETTINGS')
# Read the config vars one by one from the env vars prefixed with `PERSONAL_`.
except RuntimeError:
    class _Config:
        @classmethod
        def configure(cls):
            for k, v in os.environ.iteritems():
                if k.startswith('PERSONAL_'):
                    setattr(cls, k[9:], v)
            return cls
    app.config.from_object(_Config.configure())


CsrfProtect().init_app(app)
mail = Mail()
mail.init_app(app)
cache = FileSystemCache(app.config["CACHE_DIR"])


def get_profile():
    profile = cache.get('profile')
    if profile is None:
        profile = getattr(g, '_profile', None)
        if not profile:
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
                    'recommendations-received',
                    'projects'
                ])
                # profile picture
                profile['pictureUrls'] = application.get_picture_urls()
                cache.set('profile', profile, timeout=30 * 24 * 60 * 60)  # 30 days timeout
            except LinkedInError as e:
                profile = []
                app.logger.warning('Caught an exception while trying to get the linkedin profile: %s' % e)
            g._profile = profile
    return profile


profile = LocalProxy(get_profile)


@app.route('/')
def index():
    form = ShortMessageForm()
    return render_template('index.html', profile=profile, form=form)


@app.route('/send_message', methods=['POST'])
def message():
    if request.is_xhr:
        form = ShortMessageForm()
        if not form.validate():
            return render_template('short_message_form.html', form=form)
        # send an email if the form is valid
        msg = Message("I've just sent you a message from your personal site",
                      recipients=[app.config['EMAIL']],
                      reply_to=form.email.data)
        msg.body = form.message.data
        mail.send(msg)
        return '<div class="alert alert-success">Thank you for your message.' \
               ' I will try to reply as soon as possible.</div>'
    abort(404)


@app.route('/get_pdf')
def pdf():
    pdf = compose_pdf(profile)
    response = make_response(pdf)
    response.headers['Content-Disposition'] = 'attachment; filename="%s %s.pdf"' % (profile['firstName'],
                                                                                    profile['lastName'])
    response.mimetype = 'application/pdf'
    return response


@app.route('/clear_cache')
def clear_cache():
    cache.clear()
    flash("Cache cleared")
    return redirect(url_for('index'))


@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404


if __name__ == '__main__':
    app.run(host=app.config['HOST'])
