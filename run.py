from flask import Flask
from flask_restful import Resource, Api

from app.api import RailMitraAPI

app = Flask(__name__)
api = Api(app)

# api.add_resource(RailMitraAPI, '/thisissecret75aef2b9-073e-458d-9cd6-e3e7795ea9c2')
api.add_resource(RailMitraAPI, '/')

if __name__ == '__main__':
    app.run(debug=True)
