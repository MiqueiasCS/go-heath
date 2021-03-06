from flask import Blueprint
from flask_jwt_extended import jwt_required
from app.controllers.professional_controllers import create, delete, get_all, get_by_id, get_schedules, get_free_schedules, update, delete
from app.controllers.client_controllers import schedule_appointment


bp_professional = Blueprint(
    'bp_professional', __name__, url_prefix='/professional')

bp_professional.post('')(create)
bp_professional.get('')(get_all)
bp_professional.get('/<int:id>')(jwt_required()(get_by_id))
bp_professional.get('/<int:id>/schedules')(get_schedules)
bp_professional.post('/<int:id>/free_schedules')(get_free_schedules)
bp_professional.post('/<int:id>/schedule_appointment')(jwt_required()(schedule_appointment))
bp_professional.patch('')(jwt_required()(update))
bp_professional.delete('')(jwt_required()(delete))
