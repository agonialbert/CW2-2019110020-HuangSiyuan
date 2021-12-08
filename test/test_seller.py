# import unittest
# from flask import current_app, url_for
# from apps import app, db, bcrypt
# from apps.models import *
# from test.base import BaseTestCase
#
#
# class AdminTestCase(BaseTestCase):
#
#     def test_new_post(self):
#         response = self.client.get(url_for('seller_add'))
#         data = response.get_data(as_text=True)
#         self.assertIn('Product Add', data)
#         # open the web correctly
#         response = self.client.post(url_for('seller_add'), data=dict(
#         ), follow_redirects=True)
#         data = response.get_data(as_text=True)
#         self.assertIn('Add successfully', data)
