# auth.py
from functools import wraps
from flask import request, jsonify, g
from extensions import tenants_collection

def require_api_key(f):
    """Decorator to require a valid API key from the tenants collection."""
    @wraps(f)
    def decorated(*args, **kwargs):
        api_key = request.headers.get("X-API-Key")
        if not api_key:
            return jsonify({"error": "Unauthorized: API key missing"}), 401

        tenant = tenants_collection.find_one({"api_key": api_key})
        if not tenant:
            return jsonify({"error": "Unauthorized: Invalid API key"}), 401

        # Store the tenant_id in Flask's global context
        g.tenant = tenant["tenant_id"]
        return f(*args, **kwargs)
    return decorated
