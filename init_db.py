import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from app import create_app
from app.extensions import db
from app.models import User

app = create_app()

with app.app_context():
    db.create_all()

    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin = User(
            username='admin',
            real_name='系统管理员',
            email='admin@school.edu',
            role='admin'
        )
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        print('数据库初始化完成！')
        print('管理员账号: admin')
        print('管理员密码: admin123')
    else:
        print('数据库已存在，跳过初始化')
