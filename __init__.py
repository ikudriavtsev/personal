from flask import Flask, render_template, request
from linkedin import linkedin
from linkedin.exceptions import BaseLinkedInError
import os


app = Flask(__name__)
if 'PERSONAL_APP_SETTINGS' in os.environ:
    app.config.from_envvar('PERSONAL_APP_SETTINGS')


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
            'member-url-resources',
            'phone-numbers',
            'public-profile-url',
            # profile picture
            'picture-url',
            'picture-urls',
            'location',
            'skills',
            'educations',
        ])
    except BaseLinkedInError as e:
        profile = None
        app.logger.warning('Caught an exception while trying to get the linkedin profile: %s' % e)
    return render_template('index.html', profile=profile)


@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404


if __name__ == '__main__':
    app.run()
