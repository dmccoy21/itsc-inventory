from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User, InventoryIn, InventoryOut
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_user, login_required, logout_user, current_user
from datetime import datetime, timedelta


auth = Blueprint('auth', __name__)


# creates admin
def create_admin():
    admin = User(email="admin@email.com", first_name="admin", last_name="user",
                 password=generate_password_hash("root", method='sha256'),
                 department="LEAD")
    db.session.add(admin)
    db.session.commit()


@auth.route('/login', methods=['GET', 'POST'])
def login():
    # this will create admin upon database rebuilds
    admin = User.query.filter_by(first_name="admin").first()
    if admin:
        pass
    else:
        create_admin()

    # if user is submitting login form
    if request.method == 'POST':
        # get email
        email = request.form.get('email')
        # get password
        password = request.form.get('password')
        # find first instance of user with email
        user = User.query.filter_by(email=email).first()
        if user:
            # check the password hashes - sha256
            if check_password_hash(user.password, password):
                # success message for login
                flash('Logged In Successfully!', category='success')
                # log user in
                login_user(user, remember=True)
                # redirect to home page
                return redirect(url_for('routes.home'))
            else:
                # error message for password
                flash('Incorrect password, try again.', category='error')
        else:
            # error message for email not in database
            flash('E-mail does not exist.', category='error')
    # restart page to try again
    return render_template("login.html", user=current_user)


@auth.route('/logout')
@login_required
def logout():
    # log user out
    logout_user()
    # return to login page, restricts access to other pages
    flash('Logged Out!', category='success')
    return redirect(url_for('auth.login'))


@auth.route('/calendar', methods=['GET', 'POST'])
@login_required
def calendar():
    # redirect to calendar page
    return render_template("calendar.html", user=current_user)


@auth.route('/tech/set_up_user', methods=['GET', 'POST'])
@login_required  #
def sign_up():
    users = User.query.order_by(User.last_name).all()
    if current_user.department == 'MANAGER' or current_user.department == 'LEAD':
        if request.method == 'POST':  # un-tab if need to rebuild database
            # get form variables
            email = request.form.get('email')
            first_name = request.form.get('first_name')
            last_name = request.form.get('last_name')
            password1 = request.form.get('password1')
            password2 = request.form.get('password2')
            department = request.form.get('department')
            # check if email already in database
            user = User.query.filter_by(email=email).first()
            if user:
                flash('Email already exists.', category='error')
            elif len(email) < 5:
                flash('Email must be greater than 5 characters.', category='error')
            elif len(first_name) < 3:
                flash('First name must be greater than 3 character.', category='error')
            elif len(last_name) < 3:
                flash('Last name must be greater than 3 character.', category='error')
            elif password1 != password2:
                flash('Passwords don\'t match.', category='error')
            elif len(password1) < 5:
                flash('Password must be at least 5 characters.', category='error')
            else:
                new_user = User(email=email, first_name=first_name, last_name=last_name, password=generate_password_hash(
                    password1, method='sha256'), department=department)
                db.session.add(new_user)
                db.session.commit()
                flash('Account Created!', category='success')
                return redirect(url_for('routes.home'))
    else:
        flash('Access Restricted', category='error')
        return redirect(url_for('routes.home'))  #
    return render_template("signup.html", user=current_user, users=users)


@auth.route('/tech/view_users')
@login_required
def view_users():
    users = User.query.order_by(User.last_name).all()

    out = InventoryOut.query.order_by(InventoryOut.user_email.asc()).all()
    if current_user.department == 'MANAGER' or current_user.department == 'ITSC' or current_user.department == 'LEAD':
        flash('Now Viewing Updated Database', category='success')
        out = InventoryOut.query.order_by(InventoryOut.user_email.asc()).all()
        return render_template("view.html", user=current_user, users=users, out=out)
    else:
        flash('Access Restricted', category='error')
        return redirect(url_for('routes.home'))
    return render_template("view.html", user=current_user, users=users, out=out)


@auth.route('/tech/item_log', methods=['GET', 'POST'])
@login_required
def log_item():
    inventory_in = InventoryIn.query.order_by(InventoryIn.item_type.asc()).all()
    inventory_out = InventoryOut.query.order_by(InventoryOut.item_type.asc()).all()
    lead = User.query.filter_by(department='LEAD').first()

    full_inventory = []
    for x in inventory_in:
        full_inventory.append(x)

    for x in inventory_out:
        full_inventory.append(x)

    item_types = []
    for x in inventory_in:
        if x.item_type not in item_types:
            item_types.append(x.item_type)

    for x in inventory_out:
        if x.item_type not in item_types:
            item_types.append(x.item_type)

    item_names = []
    for x in inventory_in:
        if x.item_name not in item_names:
            item_names.append(x.item_name)

    for x in inventory_out:
        if x.item_name not in item_names:
            item_names.append(x.item_name)

    item_counts = []
    for x in item_names:
        counter = 0
        for y in full_inventory:
            if x == y.item_name:
                counter += 1
        item_counts.append(counter)

    if current_user.department == 'MANAGER' or current_user.department == 'ITSC' or current_user.department == 'LEAD':
        if request.method == 'POST':
            item_name = request.form.get('item_name')
            item_number = request.form.get('item_number')
            item_type = request.form.get('item_type')
            new_item = InventoryIn(item_name=item_name,
                                   item_number=int(item_number),
                                   item_type=item_type,
                                   dateIn=datetime.utcnow()-timedelta(hours=5))
            db.session.add(new_item)
            db.session.commit()
            flash('Item Registered!', category='success')
            return redirect(url_for('auth.log_item'))
    else:
        flash('Access Restricted', category='error')
        return redirect(url_for('routes.home'))
    return render_template("item_log.html", user=current_user, lead=lead,
                           item_names=item_names, item_counts=item_counts, item_types=item_types,
                           full_inventory=full_inventory, min=min(item_counts))


@auth.route('/tech/equipment_log', methods=['GET', 'POST'])
@login_required
def view_inventory():
    available = InventoryIn.query.order_by(InventoryIn.item_type.asc(), InventoryIn.item_number).all()
    users = User.query.order_by(User.last_name).all()
    out = InventoryOut.query.order_by(InventoryOut.item_type.asc(), InventoryOut.item_number).all()

    flash('Now Viewing Updated Inventory', category='success')
    if current_user.department == 'MANAGER' or current_user.department == 'ITSC' or current_user.department == 'LEAD':

        if request.method == 'POST':
            item_type = request.form.get('item_type')
            item_name = request.form.get('item_name')
            item_number = request.form.get('item_number')
            email = request.form.get('email')
            returnDate = request.form.get('event-date')
            process_date = returnDate.replace('T', '-').replace(':', '-').split('-')
            process_date = [int(v) for v in process_date]
            returnDate = datetime(*process_date)

            equipment_out = InventoryOut(item_name=item_name,
                                         item_type=item_type,
                                         item_number=item_number,
                                         user_email=email,
                                         dateOut=datetime.utcnow() - timedelta(hours=5),
                                         returnDate=returnDate)
            db.session.add(equipment_out)
            db.session.commit()
            item_id = request.form.get('item_id')
            switch = InventoryIn.query.get(int(item_id))
            db.session.delete(switch)
            db.session.commit()
            out = InventoryOut.query.order_by(InventoryOut.item_type.asc(), InventoryOut.item_number).all()
            available = InventoryIn.query.order_by(InventoryIn.item_type.asc(), InventoryIn.item_number).all()

        return render_template("equipment_log.html", user=current_user, available=available, out=out, users=users)
    else:
        flash('Access Restricted', category='error')
        return redirect(url_for('routes.home'))
    return render_template("equipment_log.html", user=current_user, users=users)


@auth.route('/tech/overdue', methods=['GET', 'POST'])
@login_required
def overdue():
    users = User.query.order_by(User.last_name).all()
    out = InventoryOut.query.order_by(InventoryOut.item_type.asc(), InventoryOut.item_number).all()
    overdue = InventoryOut.query.filter(InventoryOut.returnDate < (datetime.utcnow() - timedelta(hours=5))).all()
    if current_user.department == 'MANAGER' or current_user.department == 'ITSC' or current_user.department == 'LEAD':
        return render_template("overdue.html", user=current_user, out=out, users=users, overdue=overdue)
    else:
        flash('Access Restricted', category='error')
        return redirect(url_for('routes.home'))

    return render_template("overdue.html", user=current_user, out=out, users=users)


@auth.route('/tech/today', methods=['GET', 'POST'])
@login_required
def today():
    users = User.query.order_by(User.last_name).all()
    out = InventoryOut.query.order_by(InventoryOut.item_type.asc(), InventoryOut.item_number).all()
    day = datetime.today().isoweekday()

    if day == 1:
        day = datetime.utcnow() - timedelta(hours=5)
        day = day.strftime('%A, %B %d')
    elif day == 2:
        day = datetime.utcnow() - timedelta(hours=5)
        day = day.strftime('%A, %B %d')
    elif day == 3:
        day = datetime.utcnow() - timedelta(hours=5)
        day = day.strftime('%A, %B %d')
    elif day == 4:
        day = datetime.utcnow() - timedelta(hours=5)
        day = day.strftime('%A, %B %d')
    elif day == 5:
        day = datetime.utcnow() - timedelta(hours=5)
        day = day.strftime('%A, %B %d')
    elif day == 6:
        day = datetime.utcnow() - timedelta(hours=5)
        day = day.strftime('%A, %B %d')
    elif day == 7:
        day = datetime.utcnow() - timedelta(hours=5)
        day = day.strftime('%A, %B %d')

    if current_user.department == 'MANAGER' or current_user.department == 'ITSC' or current_user.department == 'LEAD':
        return render_template("today.html", user=current_user, out=out, users=users, today=day)
    else:
        flash('Access Restricted', category='error')
        return redirect(url_for('routes.home'))
    return render_template("today.html", user=current_user, out=out, users=users, today=day)
