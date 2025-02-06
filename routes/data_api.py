# routes/data_api.py
from flask import Blueprint, request, jsonify, g
from auth import require_api_key
from extensions import data_collection

api_bp = Blueprint('data_api', __name__, url_prefix='/data-api')

@api_bp.route('/<doc_id>', methods=['POST'])
@require_api_key
def set_fields(doc_id):
    payload = request.get_json(force=True)
    if not isinstance(payload, dict):
        return jsonify({"error": "Expected a JSON object with fields to update"}), 400

    composite_id = f"{g.tenant}:{doc_id}"
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
    composite_id = f"{g.tenant}:{doc_id}"
    document = data_collection.find_one({"_id": composite_id})
    value = document.get(field, None) if document else None
    return jsonify({field: value}), 200

@api_bp.route('/<doc_id>', methods=['DELETE'])
@require_api_key
def delete_document(doc_id):
    composite_id = f"{g.tenant}:{doc_id}"
    result = data_collection.delete_one({"_id": composite_id})
    if result.deleted_count == 0:
        return jsonify({"error": "Document not found"}), 404
    return jsonify({
        "status": "success",
        "message": f"Document {doc_id} deleted."
    }), 200
