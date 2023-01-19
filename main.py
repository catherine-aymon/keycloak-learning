import json
import logging

from flask import Flask, g, request
from flask_oidc import OpenIDConnect

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.config.update({
    'SECRET_KEY': 'SomethingNotEntirelySecret',
    'TESTING': True,
    'DEBUG': True,
    'OIDC_CLIENT_SECRETS': 'client_secrets.json',
    'OIDC_ID_TOKEN_COOKIE_SECURE': False,
    'OIDC_REQUIRE_VERIFIED_EMAIL': False,
    "OIDC_SCOPES": ["openid", "email", "profile"],
    'OIDC_OPENID_REALM': 'http://localhost:5000/oidc_callback'
})
oidc = OpenIDConnect(app)


@app.route('/')
def hello():
    if oidc.user_loggedin:
        # info = oidc.user_getinfo(['email', 'openid_id'])
        info = oidc.user_getinfo(['preferred_username', 'email', 'sub'])
        print(info)
        return ('<h2>Hello, %s! <br/> <a href="/login">See private info</a> '
                ' <br/> <a href="/logout">Log out</a></h2>') % \
            oidc.user_getfield('preferred_username')
    else:
        return '<h1>Welcome! <br/> <a href="/login">Log in</a></h1>'


@app.route('/login')
@oidc.require_login
def login():
    info = oidc.user_getinfo(['email', 'preferred_username', 'sub', 'email_verified', 'profile', 'given_name',
                              'family_name', 'openid'])
    print()
    print(info)
    #  return ('Hello, %s (%s)! <a href="/">Return</a>' % (info.get('email'), info.get('openid_id')))
    return '<h2>Hello, %s (%s, %s)! <br/><a href="/api">OUR API</a><br/><a href="/">Return</a></h2>' % (
        info.get('preferred_username'), info.get('email'), info.get('sub'))


@app.route('/api')
@oidc.accept_token()
def api():
    # return json.dumps({'hello': 'Welcome %s' % g.oidc_token_info['sub']})
    return json.dumps({'message': 'Welcome %s, this is my API!' % g.oidc_id_token['preferred_username']})


@app.route('/api2')
@oidc.accept_token(True, ['sub'])
def hello_api2():
    # return json.dumps({'hello': 'Welcome %s' % g.oidc_token_info['sub']})
    return json.dumps({'hello': 'Welcome %s' % g.oidc_id_token['sub']})


# TODO find out how to remove cookies from the browser
@app.route('/logout')
def logout():
    print(g.oidc_id_token)
    oidc.logout()
    cookies = request.cookies
    print(cookies)
    return '<h2>Hi, you have been logged out!<br/> <a href="/">Return</a></h2>'


if __name__ == '__main__':
    app.run()
