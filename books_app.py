from flask import Flask, jsonify, request
from flask_swagger_ui import get_swaggerui_blueprint
import traceback
# from routes import request_api
from helper import *
from query_param_validation import *

app = Flask(__name__)

SWAGGER_URL = '/swagger'
API_URL = '/static/swagger.json'
SWAGGERUI_BLUEPRINT = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "Python-Flask-REST-APIS"
    }
)
app.register_blueprint(SWAGGERUI_BLUEPRINT, url_prefix=SWAGGER_URL)

@app.route("/books")
def hello():

    try:
        query_keys = request.args.keys()
        if not validate_query_params(query_keys):
            return jsonify(invalid_request_response()), 400

        data = handle_request(request)
        return jsonify(data), 200

    except Exception as e:
        print(traceback.format_exc())
        return server_error_response(), 500


if __name__ == "__main__":
    app.run(host='0.0.0.0')




