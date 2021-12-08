# import unittest
# from flask import current_app, url_for
# from apps import app, db, bcrypt
# from apps.models import *
#
#
# class BaseTestCase(unittest.TestCase):
#     def setUp(self):
#         self.app = app
#         self.context = app.test_request_context()
#         self.context.push()
#         self.client = app.test_client()
#         self.runner = app.test_cli_runner()
#         db.create_all()
#         user = User(username='test', email='test@qq.com',  password='123', gender=2, user_type=3) # 创建测试用户记录
#         db.session.add(user)
#         db.session.commit()
#
#     def tearDown(self):
#         db.drop_all()
#         self.context.pop()
#
#     def test_login(self, username=None, password=None):
#         if username is None and password is None:
#             username = 'test'
#             password = '123'
#             return self.client.post(url_for('login'), data=dict(
#                 username=username,
#                 password=password
#             ), follow_redirects=True)
#
#     def test_logout(self):
#         return self.client.get(url_for('logout'), follow_redirects=True)
