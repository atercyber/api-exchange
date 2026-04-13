import os
from flask import Flask, request, jsonify
import requests
from firebase_config import get_api, check_key, list_apis

app = Flask(__name__)

DEV_CREDIT = {
    "developer": "@atercyber",
    "telegram": "https://t.me/atercyberchannel",
    "message": "Developed by Ater Cyber"
}

@app.route('/', methods=['GET'])
def home():
    apis = list_apis()
    endpoints = {}
    for name in apis:
        endpoints[f'/api/{name}'] = f'?key=YOUR_KEY&query=VALUE'
    return jsonify({
        "credit": DEV_CREDIT,
        "endpoints": endpoints
    })

@app.route('/api/<service_name>', methods=['GET'])
def dynamic_api(service_name):
    key = request.args.get('key')
    query = request.args.get('query')

    if not key:
        return jsonify({
            "credit": DEV_CREDIT,
            "error": "Key दो",
            "usage": f"/api/{service_name}?key=YOURKEY&query=VALUE"
        }), 401

    valid, msg = check_key(key, service_name)
    if not valid:
        return jsonify({"credit": DEV_CREDIT, "error": msg}), 403

    if not query:
        return jsonify({
            "credit": DEV_CREDIT,
            "error": "query parameter दो"
        }), 400

    api_data = get_api(service_name)
    if not api_data:
        return jsonify({
            "credit": DEV_CREDIT,
            "error": f"'{service_name}' service नहीं मिली"
        }), 404

    url = api_data['url']
    param = api_data['param']

    try:
        full_url = f"{url}&{param}={query}"
        response = requests.get(full_url, timeout=30)
        response.raise_for_status()
        api_response = response.json()

        # साफ data निकालो
        clean_data = api_response.get("data", api_response)
        if isinstance(clean_data, dict):
            for k in ["_powered_by", "credit", "developer", "owner", "admin", "note", "help_group"]:
                clean_data.pop(k, None)

        return jsonify({
            "credit": DEV_CREDIT,
            "service": service_name,
            "query": query,
            "data": clean_data
        })
    except Exception as e:
        return jsonify({
            "credit": DEV_CREDIT,
            "error": "API call failed",
            "details": str(e)
        }), 500

port = int(os.environ.get('PORT', 5000))
if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=port)
