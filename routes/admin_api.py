from flask import Blueprint, request, jsonify
from extensions import tenants_collection, data_collection
from config import Config
import datetime

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/add-tenant', methods=['POST'])
def add_tenant():
    admin_key = request.headers.get("X-Admin-Key")
    if admin_key != Config.ADMIN_API_KEY:
         return jsonify({"error": "Unauthorized: Invalid admin key"}), 401

    payload = request.get_json(force=True)
    tenant_id = payload.get("tenant_id")
    api_key = payload.get("api_key")
    if not tenant_id or not api_key:
         return jsonify({"error": "Missing tenant_id or api_key"}), 400

    if tenants_collection.find_one({"tenant_id": tenant_id}):
         return jsonify({"error": "Tenant already exists"}), 400

    tenants_collection.insert_one({
        "tenant_id": tenant_id,
        "api_key": api_key,
        "created_at": datetime.datetime.utcnow()
    })
    return jsonify({"status": "success", "tenant_id": tenant_id}), 200


@admin_bp.route('/remove-tenant', methods=['DELETE'])
def remove_tenant():
    """
    Remove a tenant from the system.
    
    Request JSON example:
        {
            "tenant_id": "tenant1"
        }
        
    The request must include the correct X-Admin-Key header.
    """
    admin_key = request.headers.get("X-Admin-Key")
    if admin_key != Config.ADMIN_API_KEY:
         return jsonify({"error": "Unauthorized: Invalid admin key"}), 401

    payload = request.get_json(force=True)
    tenant_id = payload.get("tenant_id")
    if not tenant_id:
         return jsonify({"error": "Missing tenant_id"}), 400

    # Check if the tenant exists.
    tenant = tenants_collection.find_one({"tenant_id": tenant_id})
    if not tenant:
         return jsonify({"error": "Tenant not found"}), 404

    # Remove the tenant from the tenants collection.
    tenants_collection.delete_one({"tenant_id": tenant_id})

    # Optionally, remove all documents belonging to this tenant from the data collection.
    # This assumes your documents have an _id in the format "tenant:doc_id".
    data_collection.delete_many({"_id": {"$regex": f"^{tenant_id}:"}})

    return jsonify({
        "status": "success",
        "message": f"Tenant {tenant_id} and all associated data have been removed."
    }), 200