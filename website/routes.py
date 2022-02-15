from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import login_required, current_user
from .models import User, Ticket, InventoryIn, InventoryOut
from . import db
import json
from datetime import datetime, timedelta


routes = Blueprint('routes', __name__)


@routes.route('/', methods={'GET', 'POST'})
@routes.route('/home', methods=['GET', 'POST'])
@login_required
def home():
    tickets = Ticket.query.all()
    users = User.query.all()
    if request.method == 'POST':
        ticket = request.form.get('ticket')

        if len(ticket) < 1:
            flash('Blank Ticket', category='error')
        else:
            new_ticket = Ticket(data=ticket,
                                user_id=current_user.id,
                                date=datetime.utcnow()-timedelta(hours=5))
            db.session.add(new_ticket)
            db.session.commit()
            flash('Ticket added!', category='success')

    return render_template("home.html", user=current_user, tickets=tickets, users=users)


@routes.route('/delete-ticket', methods=['POST'])
def delete_ticket():
    ticket = json.loads(request.data)
    ticketId = ticket['ticketId']
    ticket = Ticket.query.get(ticketId)
    if ticket:
        if ticket.user_id == current_user.id or current_user.department == 'MANAGER':
            db.session.delete(ticket)
            db.session.commit()
            if ticket.user_id == current_user.id:
                flash('Ticket DELETED!', category='error')
            if current_user.department == 'MANAGER':
                flash('Ticket CLOSED!', category='success')

    return jsonify({})


@routes.route('/tech/view_users/delete-user', methods=['GET', 'POST'])
def delete_user():
    user = json.loads(request.data)
    userId = user['userId']
    user = User.query.get(int(userId))
    if user:
        db.session.delete(user)
        db.session.commit()

    return jsonify({})


@routes.route('/tech/equipment_log/sign-out', methods=['POST'])
def sign_out():
    item = json.loads(request.data)
    itemId = item['itemId']
    item = InventoryIn.query.get(int(itemId))
    if item:
        db.session.delete(item)
        db.session.commit()
        flash('Item DELETED!', category='error')

    return jsonify({})


@routes.route('/tech/equipment_log/sign-in', methods=['POST'])
def sign_in():
    item = json.loads(request.data)
    itemId = item['itemId']
    item = InventoryOut.query.get(int(itemId))
    if item:
        db.session.delete(item)
        db.session.commit()
        flash('Item REMOVED!', category='success')
        new_item = InventoryIn(item_name=item.item_name,
                               item_type=item.item_type,
                               item_number=item.item_number,
                               dateIn=datetime.utcnow()-timedelta(hours=5))
        db.session.add(new_item)
        db.session.commit()

    return jsonify({})
