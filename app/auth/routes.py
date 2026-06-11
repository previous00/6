from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user
from app.auth import auth_bp
from app.extensions import db
from app.models import User
from app.forms import LoginForm, RegisterForm


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            if not user.is_active:
                flash('账户已被禁用，请联系管理员', 'danger')
                return redirect(url_for('auth.login'))
            login_user(user)
            flash('登录成功', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('main.index'))
        flash('用户名或密码错误', 'danger')
    return render_template('auth/login.html', form=form)


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            real_name=form.real_name.data,
            email=form.email.data,
            role=form.role.data
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('注册成功，请登录', 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form)


@auth_bp.route('/logout')
def logout():
    logout_user()
    flash('已退出登录', 'info')
    return redirect(url_for('main.index'))
