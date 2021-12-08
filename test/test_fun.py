# import unittest
# from apps import app, db, bcrypt
# from apps.models import *
# from flask import url_for
#
#
# class ApiTestCase(unittest.TestCase):
#     def setUp(self):
#         self.app = app
#         self.client = self.app.test_client()
#         self.db = db
#
#
#     def test_addCart(self):
#         response = self.client.post(
#             "/register",
#             data={
#                 "email": "2292751150@qq.com",
#                 "password": "123",
#                 "username": "123",
#                 "csrf_token": "ImU3MzNmZWVmMmJlYjU4OTI5Mzk5OGFiZTc1NWViYWRlMjdkZWExNzgi.Ya8_jw.lmjvnGgYJa8ZxmRO8oXKYPgoNvo"
#             }
#         )
#
