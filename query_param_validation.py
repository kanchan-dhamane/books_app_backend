from config import *


def validate_query_params(keys):
    for key in keys:
        if key not in VALID_QUERY_PARAMS:
            return False

    return True


def invalid_request_response():
    return {
        "message": "Invalid query params",
        "valid query params": VALID_QUERY_PARAMS
    }


def server_error_response():
    return {
        "message": "Internal server error"
    }