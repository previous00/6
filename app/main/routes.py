from flask import render_template, request, current_app
from app.main import main_bp
from app.models import Activity, CATEGORIES


@main_bp.route('/')
def index():
    activities = Activity.query.filter_by(status='approved').order_by(
        Activity.created_at.desc()
    ).limit(6).all()
    return render_template('main/index.html', activities=activities, categories=CATEGORIES)


@main_bp.route('/activities')
def activity_list():
    page = request.args.get('page', 1, type=int)
    keyword = request.args.get('keyword', '')
    category = request.args.get('category', '')

    query = Activity.query.filter_by(status='approved')

    if keyword:
        query = query.filter(Activity.title.contains(keyword))
    if category:
        query = query.filter_by(category=category)

    pagination = query.order_by(Activity.start_time.desc()).paginate(
        page=page, per_page=current_app.config['ACTIVITIES_PER_PAGE'], error_out=False
    )

    return render_template('main/activity_list.html',
                           pagination=pagination,
                           activities=pagination.items,
                           keyword=keyword,
                           category=category,
                           categories=CATEGORIES)


@main_bp.route('/activities/<int:activity_id>')
def activity_detail(activity_id):
    activity = Activity.query.get_or_404(activity_id)
    return render_template('main/activity_detail.html', activity=activity, categories=CATEGORIES)
