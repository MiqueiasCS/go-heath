from flask import Blueprint
from app.controllers.professional_controllers import create, get_all, get_by_id


bp_professional = Blueprint(
    'bp_professional', __name__, url_prefix='/professional')

bp_professional.post('')(create)
bp_professional.get('')(get_all)
bp_professional.get('/<int:id>')(get_by_id)
