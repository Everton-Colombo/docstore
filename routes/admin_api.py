from flask import Blueprint, request, jsonify
from extensions import tenants_collection
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
