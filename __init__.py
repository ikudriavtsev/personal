from flask import Flask, render_template
import os


app = Flask(__name__)
app.debug = True

if 'PERSONAL_APP_SETTINGS' in os.environ:
    app.config.from_envvar('PERSONAL_APP_SETTINGS')

@app.route('/')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    app.run()
