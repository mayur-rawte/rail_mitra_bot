import os

from run import app as application

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(port)
    application.run(host='0.0.0.0', port=port)
