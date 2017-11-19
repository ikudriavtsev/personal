# Personal web site

This small [Flask](http://flask.pocoo.org/) application is my personal web site.
It displays the data from [LinkedIn](http://developer.linkedin.com/) profile.
It also generates CV - a PDF file - on the fly.

## Installation

Simply clone this repo and install the dependencies from `requirements.txt`.
Make sure, that this [PR](https://github.com/ozgur/python-linkedin/pull/34) is included into the [python-linkedin](https://github.com/ozgur/python-linkedin) distribution.

## Configuration

There is a sample config file included. You can get the details from comments in that file, from Flask [docs](http://flask.pocoo.org/docs/config/) and from Flask-Mail [docs](http://packages.python.org/Flask-Mail/#configuring-flask-mail).
The config of the LinkedIn application is however simplified - to avoid making the visitor authenticate via LinkedIn to view the profile, the token and secret, that are generated with the LinkedIn app creation, are used.

## Run

Here is the quick command how to run the site:

```
cd path/to/repo
PERSONAL_APP_SETTINGS=config.cfg python personal.py
```
