from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from functools import wraps
from app.organizer import organizer_bp
from app.extensions import db
from app.models import Activity, Registration, CATEGORIES
from app.forms import ActivityForm


def organizer_required(f):
    @wraps(f)
    @login_required
    def decorated(*args, **kwargs):
        if current_user.role != 'organizer':
            flash('无权访问', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated


@organizer_bp.route('/dashboard')
@organizer_required
def dashboard():
    activities = Activity.query.filter_by(organizer_id=current_user.id).order_by(
        Activity.created_at.desc()
    ).all()
    return render_template('organizer/dashboard.html', activities=activities, categories=CATEGORIES)


@organizer_bp.route('/activities/create', methods=['GET', 'POST'])
@organizer_required
def create_activity():
    form = ActivityForm()
    if form.validate_on_submit():
        activity = Activity(
            title=form.title.data,
            category=form.category.data,
            description=form.description.data,
            location=form.location.data,
            start_time=form.start_time.data,
            end_time=form.end_time.data,
            max_participants=form.max_participants.data,
            registration_deadline=form.registration_deadline.data,
            organizer_id=current_user.id
        )
        db.session.add(activity)
        db.session.commit()
        flash('活动创建成功，等待管理员审核', 'success')
        return redirect(url_for('organizer.dashboard'))
    return render_template('organizer/activity_form.html', form=form, title='创建活动')


@organizer_bp.route('/activities/<int:activity_id>/edit', methods=['GET', 'POST'])
@organizer_required
def edit_activity(activity_id):
    activity = Activity.query.get_or_404(activity_id)
    if activity.organizer_id != current_user.id:
        flash('无权编辑此活动', 'danger')
        return redirect(url_for('organizer.dashboard'))

    form = ActivityForm(obj=activity)
    if form.validate_on_submit():
        activity.title = form.title.data
        activity.category = form.category.data
        activity.description = form.description.data
        activity.location = form.location.data
        activity.start_time = form.start_time.data
        activity.end_time = form.end_time.data
        activity.max_participants = form.max_participants.data
        activity.registration_deadline = form.registration_deadline.data
        if activity.status == 'rejected':
            activity.status = 'pending'
            activity.reject_reason = None
        db.session.commit()
        flash('活动更新成功', 'success')
        return redirect(url_for('organizer.dashboard'))
    return render_template('organizer/activity_form.html', form=form, title='编辑活动')


@organizer_bp.route('/activities/<int:activity_id>/delete', methods=['POST'])
@organizer_required
def delete_activity(activity_id):
    activity = Activity.query.get_or_404(activity_id)
    if activity.organizer_id != current_user.id:
        flash('无权删除此活动', 'danger')
        return redirect(url_for('organizer.dashboard'))

    Registration.query.filter_by(activity_id=activity.id).delete()
    db.session.delete(activity)
    db.session.commit()
    flash('活动已删除', 'success')
    return redirect(url_for('organizer.dashboard'))


@organizer_bp.route('/activities/<int:activity_id>/participants')
@organizer_required
def participants(activity_id):
    activity = Activity.query.get_or_404(activity_id)
    if activity.organizer_id != current_user.id:
        flash('无权查看此活动', 'danger')
        return redirect(url_for('organizer.dashboard'))

    registrations = Registration.query.filter_by(
        activity_id=activity.id, status='registered'
    ).all()
    return render_template('organizer/participants.html', activity=activity, registrations=registrations)


@organizer_bp.route('/activities/<int:activity_id>/remove-participant/<int:reg_id>', methods=['POST'])
@organizer_required
def remove_participant(activity_id, reg_id):
    activity = Activity.query.get_or_404(activity_id)
    if activity.organizer_id != current_user.id:
        flash('无权操作', 'danger')
        return redirect(url_for('organizer.dashboard'))

    reg = Registration.query.get_or_404(reg_id)
    reg.status = 'cancelled'
    db.session.commit()
    flash('已移除该参与者', 'success')
    return redirect(url_for('organizer.participants', activity_id=activity_id))
