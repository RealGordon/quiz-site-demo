from flask import Flask
import os
SUKUU_SECRET=os.environ["SUKUU_SECRET"]
def create_app(test_config=None):
    
     # create and configure the app
    from . import settings
    if settings.SUKUU_LOCAL:
        class MyFlask(Flask):
            def get_send_file_max_age(self, name):
                lower=name.lower()
                if lower.endswith('.js'):
                    from flask import request
                    if '/sukuu/' in request.path:
                        return 3
                elif lower.endswith('.html') :
                    return 3
                return Flask.get_send_file_max_age(self, name)
        app = MyFlask('sukuu', instance_relative_config=True)
        app.static_folder=settings.LOCAL_STATIC_FOLDER
        app.static_url_path='/static'
    else:
        app = Flask('sukuu', instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY=SUKUU_SECRET)

        #DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'))
    

  #  if test_config is None:
        # load the instance config, if it exists, when not testing
  #      app.config.from_pyfile('config.py', silent=True)
  #  else:
        # load the test config if passed in
   #     app.config.from_mapping(test_config)

    # ensure the instance folder exists
    #try:
        #os.makedirs(app.instance_path)
    #except OSError:
        #pass
    
    from . import (firestoredbquiz,facebookauth,
                   home,confess,mailing,test,testupdate)
    app.register_blueprint(facebookauth.auth)
    app.register_blueprint(home.bp) 
    app.register_blueprint(firestoredbquiz.bp)
    app.register_blueprint(mailing.bp)
    app.register_blueprint(confess.bp)
    app.register_blueprint(testupdate.bp)
    app.register_blueprint(test.bp)
    
    
    
    return app
