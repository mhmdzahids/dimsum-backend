import logging
from flask import Blueprint, request
from app.shared.response import api_success, api_error
from app.modules.banners.service import BannerService
from app.core.security import admin_required

logger = logging.getLogger(__name__)
banners_bp = Blueprint('banners', __name__)

@banners_bp.route('', methods=['GET'])
def get_banners():
    active_only = request.args.get('active_only', 'false').lower() == 'true'
    banners = BannerService.get_all(active_only=active_only)
    return api_success(data=[b.to_dict() for b in banners])

@banners_bp.route('', methods=['POST'])
@admin_required
def upload_banner():
    if 'image' not in request.files:
        return api_error('No image file provided', 400)
        
    file = request.files['image']
    
    try:
        banner = BannerService.save_banner(file)
        return api_success(data=banner.to_dict(), status=201, message='Banner uploaded successfully')
    except ValueError as e:
        return api_error(str(e), 400)
    except Exception as e:
        logger.exception("Banner upload failed")
        return api_error('Upload failed due to an internal error', 500)

@banners_bp.route('/<banner_id>', methods=['DELETE'])
@admin_required
def delete_banner(banner_id):
    try:
        BannerService.delete(banner_id)
        return api_success(message='Banner deleted successfully')
    except ValueError as e:
        return api_error(str(e), 404)
    except Exception as e:
        logger.exception(f"Banner deletion failed for {banner_id}")
        return api_error('Delete failed due to an internal error', 500)
