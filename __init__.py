from flask import Flask, render_template, request
from linkedin import linkedin
import os


app = Flask(__name__)
app.debug = True

if 'PERSONAL_APP_SETTINGS' in os.environ:
    app.config.from_envvar('PERSONAL_APP_SETTINGS')

@app.route('/')
def index():
    authentication = linkedin.LinkedInDeveloperAuthentication(
        app.config['API_KEY'],
        app.config['API_SECRET'],
        app.config['USER_TOKEN'],
        app.config['USER_SECRET'],
        request.base_url,
        linkedin.PERMISSIONS.enums.values())
    application = linkedin.LinkedInApplication(authentication)
    profile = application.get_profile()
    print profile
    return render_template('index.html')


if __name__ == '__main__':
    app.run()
