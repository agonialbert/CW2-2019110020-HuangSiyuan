import sqlite3
import unittest
from apps import app,db,bcrypt
from apps.models import *
from flask import url_for

import os.path

class ApiTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.client = self.app.test_client()
        self.db = db

    def test_user_exists(self):
        email = "2292751150@qq.com"
        password = "123"
        user = User.query.filter_by(email=email).first()
        exists = False
        if user :
            exists = bcrypt.check_password_hash(user.password, password)
        print("user: ",user)

        self.assertTrue(exists)

    def test_product_exists(self):
        product = Product(title='test', price=120, description='for test', image_file='1.jpg', category_id=1, seller_id=3)
        db.session.add(product)
        db.session.commit()
        product_test = Product.query.filter_by(title='test').first()
        self.assertIsNotNone(product_test)



