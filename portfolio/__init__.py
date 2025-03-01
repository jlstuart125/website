import os

from flask import Flask

"""This is an 'application factory' function."""
def create_app(test_config=None) -> Flask:
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',    # This set the secret key for the debugger - would be bad to have this outside of development.
        DATABASE=os.path.join(app.instance_path, 'stuart.sqlite'),
    )

    '''
       The following lines will overrite the config defined above - applying the actual secret key.
    '''
    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # a simple page that says hello
    @app.route('/hello')
    def hello() -> str:
        return 'Hello, World!'

    from . import db
    db.init_app(app)

    from . import auth
    app.register_blueprint(auth.bp)

    from . import blog
    app.register_blueprint(blog.bp)
    '''associate this endpoint with the '/' url - making it so that
    url_for("index") == url_for("blog.index")
    '''
    
    app.add_url_rule("/", endpoint="index")

    return app