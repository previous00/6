from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from functools import wraps
from app.admin import admin_bp
from app.extensions import db
from app.models import Activity, User, Registration, CATEGORIES
from app.forms import RejectForm, ActivityForm


def admin_required(f):
    @wraps(f)
    @login_required
    def decorated(*args, **kwargs):
        if current_user.role != 'admin':
            flash('无权访问', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated


@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    pending_count = Activity.query.filter_by(status='pending').count()
    approved_count = Activity.query.filter_by(status='approved').count()
    user_count = User.query.count()
    registration_count = Registration.query.filter_by(status='registered').count()
    return render_template('admin/dashboard.html',
                           pending_count=pending_count,
                           approved_count=approved_count,
                           user_count=user_count,
                           registration_count=registration_count)


@admin_bp.route('/reviews')
@admin_required
def review_list():
    page = request.args.get('page', 1, type=int)
    pagination = Activity.query.filter_by(status='pending').order_by(
        Activity.created_at.desc()
    ).paginate(page=page, per_page=10, error_out=False)
    return render_template('admin/review_list.html', pagination=pagination, activities=pagination.items, categories=CATEGORIES)


@admin_bp.route('/reviews/<int:activity_id>/approve', methods=['POST'])
@admin_required
def approve_activity(activity_id):
    activity = Activity.query.get_or_404(activity_id)
    activity.status = 'approved'
    activity.reject_reason = None
    db.session.commit()
    flash(f'活动「{activity.title}」已通过审核', 'success')
    return redirect(url_for('admin.review_list'))


@admin_bp.route('/reviews/<int:activity_id>/reject', methods=['POST'])
@admin_required
def reject_activity(activity_id):
    activity = Activity.query.get_or_404(activity_id)
    reason = request.form.get('reject_reason', '')
    if not reason:
        flash('请填写驳回原因', 'warning')
        return redirect(url_for('admin.review_list'))
    activity.status = 'rejected'
    activity.reject_reason = reason
    db.session.commit()
    flash(f'活动「{activity.title}」已驳回', 'info')
    return redirect(url_for('admin.review_list'))


@admin_bp.route('/users')
@admin_required
def user_list():
    page = request.args.get('page', 1, type=int)
    pagination = User.query.order_by(User.created_at.desc()).paginate(
        page=page, per_page=15, error_out=False
    )
    return render_template('admin/user_list.html', pagination=pagination, users=pagination.items)


@admin_bp.route('/users/<int:user_id>/toggle', methods=['POST'])
@admin_required
def toggle_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash('不能禁用自己的账户', 'warning')
        return redirect(url_for('admin.user_list'))
    user.is_active_user = not user.is_active_user
    db.session.commit()
    status = '启用' if user.is_active_user else '禁用'
    flash(f'用户「{user.real_name}」已{status}', 'success')
    return redirect(url_for('admin.user_list'))


@admin_bp.route('/activities/create', methods=['GET', 'POST'])
@admin_required
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
            organizer_id=current_user.id,
            status='approved'
        )
        db.session.add(activity)
        db.session.commit()
        flash('活动创建成功（已自动通过审核）', 'success')
        return redirect(url_for('admin.dashboard'))
    return render_template('admin/activity_form.html', form=form)
