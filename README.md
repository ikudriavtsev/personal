# Personal web site

This small [Flask](http://flask.pocoo.org/) application is my personal web site.
It generates the site using data, that pulls from [LinkedIn](http://developer.linkedin.com/) profile.
It also creates a PDF file on the fly.

## Installation

Simply clone this repo and install the dependencies from `requirements.txt`.
Make sure, that this [PR](https://github.com/ozgur/python-linkedin/pull/34) is included into the [python-linkedin](https://github.com/ozgur/python-linkedin) distribution.

## Configuration

There is a sample config file included. You can get the details from comments in that file, from Flask [docs](http://flask.pocoo.org/docs/config/) and from Flask-Mail [docs](http://packages.python.org/Flask-Mail/#configuring-flask-mail).
The config of the LinkedIn application is however simplyfied - to avoid making the visitor authenticate via LinkedIn to view the profile, the token and secret, that are generated with the LinkedIn app creation, are used. These token-secret pair is valid for 60 days only, so one should re-generate them every time upon expiration. For this reason I'm considering moving to some other professional network that gives more flexible API.

## Run

Here is the quick command how to run the site:

```
cd path/to/repo
export PERSONAL_APP_SETTINGS='path/to/repo/config.cfg.sample' && python personal.py
```
You can get more info from the Flask [docs](http://flask.pocoo.org/docs/).
