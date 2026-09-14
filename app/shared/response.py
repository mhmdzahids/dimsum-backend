from flask import jsonify

def api_success(data=None, message=None, status=200):
    body = {'success': True}
    if data is not None:
        body['data'] = data
    if message:
        body['message'] = message
    return jsonify(body), status

def api_error(error, status=400, errors=None):
    body = {'success': False, 'error': error}
    if errors:
        body['errors'] = errors
    return jsonify(body), status
