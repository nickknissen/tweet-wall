import os
from tweet_wall import create_app

if __name__ == '__main__':
    app = create_app()
    app.debug = os.getenv("TW_DEBUG")
    app.run(host='0.0.0.0')
