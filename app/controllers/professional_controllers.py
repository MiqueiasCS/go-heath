from flask import jsonify, request, current_app
from app.exceptions.schedules_exceptions import MultipleKeysFreeSchedulesError, MissingKeyError, ProfessionalNotFoundError, ProfessionalScheduleListError, TypeDateNotAllowedError
from app.models.client_model import ClientModel
from app.models.professional_model import ProfessionalModel
from flask_jwt_extended import get_jwt_identity
from werkzeug.security import generate_password_hash
from app.exceptions.professional_exceptions import NotFoundProfessionalError, KeysNotAllowedError, TypeValueError, InvalidDateFormatError, MissingFieldError, TypeKeyEmailError, TypeKeyPhoneError
from app.exceptions.food_plan_exceptions import NotFoundError
from datetime import *
import sqlalchemy
from app.controllers import check_user, format_output_especific_professional, validate_keys_professional, validate_type_value_professional, check_all_fields_professional, check_type_and_format_email, check_type_and_format_phone
from app.models.calendar_table import CalendarModel


def create():

    data = request.get_json()
    data['final_rating'] = 0

    data['final_rating'] = 0

    try:
        check_all_fields_professional(data)
        validate_keys_professional(data)
        validate_type_value_professional(data)
        check_type_and_format_email(data)
        check_type_and_format_phone(data)

        session = current_app.db.session

        if type(data['name']) != str:
            raise TypeValueError('name', data['name'])

        password_to_hash = data.pop("password")
        professional = ProfessionalModel(**data)
        professional.password = password_to_hash

        session.add(professional)
        session.commit()

        return jsonify(professional), 200

    except sqlalchemy.exc.IntegrityError as err:
        errorInfo = str(err.orig.args)
        msg = errorInfo.split('Key')[1].split('.\\n')[0]
        msg = format_output_especific_professional(msg)
        return jsonify({'error': msg}), 409
    except KeysNotAllowedError as err:
        return jsonify(err.message), 400
    except TypeValueError as err:
        return jsonify(err.message), 400
    except MissingFieldError as err:
        return jsonify(err.message), 400
    except TypeKeyEmailError as err:
        return jsonify(err.message), 400
    except TypeKeyPhoneError as err:
        return jsonify(err.message), 400


def get_all():

    professional_list = ProfessionalModel.query.all()

    return jsonify(professional_list), 200


def get_by_id(id):

    try:
        professional = ProfessionalModel.query.filter_by(id=id).first()

        if not professional:
            raise NotFoundProfessionalError
        return jsonify(professional.serialize()), 200

    except NotFoundProfessionalError as err:
        return jsonify(err.message), 404


def update():

    data = request.get_json()

    try:
        validate_keys_professional(data)
        validate_type_value_professional(data)

        professional = get_jwt_identity()

        if not professional:
            raise NotFoundProfessionalError

        if 'password' in data.keys():
            password_to_hash = data.pop('password')
            data['password_hash'] = generate_password_hash(password_to_hash)

        check_type_and_format_email(data)
        check_type_and_format_phone(data)

        ProfessionalModel.query.filter_by(
            email=professional['email']).update(data)

        # current_app.db.session.commit()

        if 'password_hash' in data.keys():
            data.pop('password_hash')

        return jsonify(data), 200
    except NotFoundProfessionalError as err:
        return jsonify(err.message), 404
    except KeysNotAllowedError as err:
        return jsonify(err.message), 400
    except TypeValueError as err:
        return jsonify(err.message), 400
    except TypeKeyEmailError as err:
        return jsonify(err.message), 400
    except TypeKeyPhoneError as err:
        return jsonify(err.message), 400


def delete():

    try:
        user = get_jwt_identity()
        professional = check_user(
            user["id"], ProfessionalModel, "professional")

        current_app.db.session.delete(professional)
        current_app.db.session.commit()

    except NotFoundError as error:
        return jsonify(error.message), 404

    return "", 204


def get_schedules(id):
    schedules = CalendarModel.query.all()

    schedules_found = [
        schedule for schedule in schedules if schedule.professional_id == id]

    try:
        professional = ProfessionalModel.query.get(id)

        if professional == None:
            raise ProfessionalNotFoundError

    except ProfessionalNotFoundError as error:

        return jsonify(error.message), 404

    try:

        if len(schedules_found) <= 0:
            raise ProfessionalScheduleListError

    except ProfessionalScheduleListError as error:
        return jsonify(error.message), 200

    return jsonify([{
        'horario': schedule_found.schedule,
        'client': ClientModel.query.get(schedule_found.client_id)} for schedule_found in schedules_found

    ]), 200


def get_free_schedules(id):

    free_hours = []

    busy_schedule = []

    free_schedules = []

    data = request.get_json()

    try:
        if len(data.keys()) > 1:
            raise MultipleKeysFreeSchedulesError
    except MultipleKeysFreeSchedulesError as error:
        return jsonify(error.message), 400

    try:
        if "schedule_date" not in data.keys():
            raise MissingKeyError
    except MissingKeyError as error:
        return jsonify(error.message), 400

    try:
        if type(data['schedule_date']) != str:
            raise TypeDateNotAllowedError
    except TypeDateNotAllowedError as error:
        return jsonify(error.message), 400

    try:
        professional = ProfessionalModel.query.get(id)
        if professional == None:
            raise ProfessionalNotFoundError

    except ProfessionalNotFoundError as error:
        return jsonify(error.message), 404

    try:
        schedule_date = datetime.strptime(data['schedule_date'], "%d/%m/%Y")
    except:
        return jsonify({'msg': 'currect date format : dd/mm/YYYY'}), 400

    schedule_date = schedule_date + timedelta(hours=9)

    schedules = CalendarModel.query.filter_by(professional_id=id).all()

    if len(schedules) > 0:

        for schedule_found in schedules:
            date = (datetime.strptime(
                str(schedule_found.schedule), "%Y-%m-%d %H:%M:%S"))
            busy_schedule.append(date)

    while schedule_date.hour < 17.15:
        free_hours.append(schedule_date)
        schedule_date += timedelta(minutes=45)

    for hour in free_hours:

        if hour not in busy_schedule:
            free_schedules.append(hour)

    return jsonify([{'horario': schedule_found} for schedule_found in free_schedules]), 200
