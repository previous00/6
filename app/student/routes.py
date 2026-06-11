from datetime import datetime
from flask import render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from functools import wraps
from app.student import student_bp
from app.extensions import db
from app.models import Activity, Registration, CATEGORIES


def student_required(f):
    @wraps(f)
    @login_required
    def decorated(*args, **kwargs):
        if current_user.role != 'student':
            flash('无权访问', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated


@student_bp.route('/register/<int:activity_id>', methods=['POST'])
@student_required
def register_activity(activity_id):
    activity = Activity.query.get_or_404(activity_id)

    if activity.status != 'approved':
        flash('该活动未开放报名', 'warning')
        return redirect(url_for('main.activity_detail', activity_id=activity_id))

    if activity.registration_deadline and datetime.utcnow() > activity.registration_deadline:
        flash('报名已截止', 'warning')
        return redirect(url_for('main.activity_detail', activity_id=activity_id))

    existing = Registration.query.filter_by(
        user_id=current_user.id, activity_id=activity_id, status='registered'
    ).first()
    if existing:
        flash('您已报名此活动', 'info')
        return redirect(url_for('main.activity_detail', activity_id=activity_id))

    if activity.is_full:
        flash('报名人数已满', 'warning')
        return redirect(url_for('main.activity_detail', activity_id=activity_id))

    cancelled = Registration.query.filter_by(
        user_id=current_user.id, activity_id=activity_id, status='cancelled'
    ).first()
    if cancelled:
        cancelled.status = 'registered'
        cancelled.registered_at = datetime.utcnow()
    else:
        reg = Registration(user_id=current_user.id, activity_id=activity_id)
        db.session.add(reg)

    db.session.commit()
    flash('报名成功', 'success')
    return redirect(url_for('main.activity_detail', activity_id=activity_id))


@student_bp.route('/cancel/<int:registration_id>', methods=['POST'])
@student_required
def cancel_registration(registration_id):
    reg = Registration.query.get_or_404(registration_id)
    if reg.user_id != current_user.id:
        flash('无权操作', 'danger')
        return redirect(url_for('student.my_registrations'))

    reg.status = 'cancelled'
    db.session.commit()
    flash('已取消报名', 'success')
    return redirect(url_for('student.my_registrations'))


@student_bp.route('/my-registrations')
@student_required
def my_registrations():
    registrations = Registration.query.filter_by(user_id=current_user.id).order_by(
        Registration.registered_at.desc()
    ).all()
    return render_template('student/my_registrations.html', registrations=registrations, categories=CATEGORIES)
