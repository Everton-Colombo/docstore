import os
from flask import Flask, request, jsonify, g, Blueprint
from functools import wraps
from pymongo import MongoClient

app = Flask(__name__)

# --- Tenant API Key Setup ---
# In production, these keys should be stored securely.
API_KEYS = {
    "secret-key-tenant1": "tenant1",
    "secret-key-tenant2": "tenant2",
}

def require_api_key(f):
    """Decorator to require a valid API key in the X-API-Key header."""
    @wraps(f)
    def decorated(*args, **kwargs):
        api_key = request.headers.get("X-API-Key")
        if not api_key or api_key not in API_KEYS:
            return jsonify({"error": "Unauthorized"}), 401
        # Store the tenant ID in Flask's global context.
        g.tenant = API_KEYS[api_key]
        return f(*args, **kwargs)
    return decorated

# --- MongoDB Setup ---
MONGO_URI = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/mydatabase')
client = MongoClient(MONGO_URI)
db = client.get_default_database()
# Use a collection named "data" to store our generic documents.
data_collection = db.data

# --- Create a Blueprint with a root path prefix ---
api_bp = Blueprint('api', __name__, url_prefix='/data-api')

@api_bp.route('/<doc_id>', methods=['POST'])
@require_api_key
def set_fields(doc_id):
    """
    Set or update fields for the document identified by doc_id.
    The document is stored with a composite _id in the format:
        "<tenant>:<doc_id>"
    
    Request body example:
        {
            "name": "Alice",
            "email": "alice@example.com"
        }
    """
    payload = request.get_json(force=True)
    if not isinstance(payload, dict):
        return jsonify({"error": "Expected a JSON object with fields to update"}), 400

    # Create a composite key to namespace documents by tenant.
    composite_id = f"{g.tenant}:{doc_id}"
    
    # Use update_one with upsert to insert or update the document.
    data_collection.update_one(
        {"_id": composite_id},
        {
            "$set": payload,
            "$setOnInsert": {"tenant": g.tenant, "doc_id": doc_id}
        },
        upsert=True
    )
    
    document = data_collection.find_one({"_id": composite_id})
    return jsonify({
        "status": "success",
        "tenant": g.tenant,
        "doc_id": doc_id,
        "data": document
    }), 200

@api_bp.route('/<doc_id>/<field>', methods=['GET'])
@require_api_key
def get_field(doc_id, field):
    """
    Retrieve the value of a specific field for the document identified by doc_id.
    Only documents for the authenticated tenant are accessible. If the document
    or field does not exist, the API returns null for the field.
    
    Example response if the field exists:
        { "email": "alice@example.com" }
    Example response if the field does not exist:
        { "email": null }
    """
    composite_id = f"{g.tenant}:{doc_id}"
    document = data_collection.find_one({"_id": composite_id})
    value = document.get(field, None) if document else None
    return jsonify({field: value}), 200

@api_bp.route('/<doc_id>', methods=['DELETE'])
@require_api_key
def delete_document(doc_id):
    """
    Delete the document identified by doc_id for the authenticated tenant.
    Returns a 404 error if the document is not found.
    """
    composite_id = f"{g.tenant}:{doc_id}"
    result = data_collection.delete_one({"_id": composite_id})
    if result.deleted_count == 0:
        return jsonify({"error": "Document not found"}), 404
    return jsonify({
        "status": "success",
        "message": f"Document {doc_id} deleted."
    }), 200

# Register the blueprint with the main Flask app.
app.register_blueprint(api_bp)

if __name__ == '__main__':
    # Listen on all interfaces, port 5000.
    app.run(host='0.0.0.0', port=5000, debug=True)
