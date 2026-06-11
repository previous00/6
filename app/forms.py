from datetime import datetime, date
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, TextAreaField, IntegerField, DateTimeLocalField, SubmitField
from wtforms.validators import DataRequired, EqualTo, Length, ValidationError, Optional
from app.models import User, CATEGORIES


class LoginForm(FlaskForm):
    username = StringField('用户名', validators=[DataRequired()])
    password = PasswordField('密码', validators=[DataRequired()])
    submit = SubmitField('登录')


class RegisterForm(FlaskForm):
    username = StringField('用户名', validators=[DataRequired(), Length(min=3, max=64)])
    real_name = StringField('真实姓名', validators=[DataRequired(), Length(max=64)])
    email = StringField('邮箱', validators=[DataRequired()])
    password = PasswordField('密码', validators=[DataRequired(), Length(min=6)])
    password2 = PasswordField('确认密码', validators=[DataRequired(), EqualTo('password', message='两次密码不一致')])
    role = SelectField('角色', choices=[('student', '学生'), ('organizer', '活动组织者')])
    submit = SubmitField('注册')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('用户名已存在')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('邮箱已被注册')


class ActivityForm(FlaskForm):
    title = StringField('活动标题', validators=[DataRequired(), Length(max=200)])
    category = SelectField('活动分类', choices=CATEGORIES, validators=[DataRequired()])
    description = TextAreaField('活动描述', validators=[DataRequired()])
    location = StringField('活动地点', validators=[Optional(), Length(max=200)])
    start_time = DateTimeLocalField('开始时间', validators=[DataRequired()])
    end_time = DateTimeLocalField('结束时间', validators=[DataRequired()])
    max_participants = IntegerField('最大报名人数（0为不限）', validators=[DataRequired()], default=0)
    registration_deadline = DateTimeLocalField('报名截止时间', validators=[Optional()])
    submit = SubmitField('提交')

    def validate_start_time(self, field):
        if field.data and field.data.date() < date.today():
            raise ValidationError('开始时间不能早于今天')

    def validate_end_time(self, field):
        if field.data and self.start_time.data:
            if field.data <= self.start_time.data:
                raise ValidationError('结束时间不能在开始时间之前')

    def validate_registration_deadline(self, field):
        if field.data:
            if field.data < datetime.now():
                raise ValidationError('报名截止时间不能早于当前时间')
            if self.start_time.data and field.data > self.start_time.data:
                raise ValidationError('报名截止时间不能在活动开始时间之后')


class RejectForm(FlaskForm):
    reject_reason = TextAreaField('驳回原因', validators=[DataRequired()])
    submit = SubmitField('驳回')
