import unittest
from flask import url_for
from apps import app, bcrypt
from apps.models import *


class BaseTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.app.config.update(
            TESTING=True,
            WTF_CSRF_ENABLED=False,
            # SQLALCHEMY_DATABASE_URI='sqlite:///:memory:'
        )
        db.create_all()
        self.context = app.test_request_context()
        self.context.push()
        self.client = app.test_client()
        self.runner = app.test_cli_runner()

    # def tearDown(self):
    #     db.session.remove()
    #     db.drop_all()

    def test_login(self, username=None, password=None):
        if username is None and password is None:
            username = 'test'
            password = '123'
            return self.client.post(url_for('login'), data=dict(
                username=username,
                password=password
            ), follow_redirects=True)
        # wrong password
        response = self.client.post('/login', data=dict(
            username='test',
            password='456'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('Login success.', data)
        self.assertIn('Invalid username or password.', data)

    def test_logout(self):
        return self.client.get(url_for('logout'), follow_redirects=True)

    def test_register(self):
        # 注册新账户
        response = self.client.post(url_for('register'), data={
            'email': 'john@example.com',
            'username': 'johnnnnnnnnnnnnnnnnnnnn',
            'password': 'cat',
            'password2': 'cat'
        })
        data = response.get_data(as_text=True)
        self.assertIn('Sign up', data)

        response = self.client.post(url_for('register'), data={
            'email': 'john@example.com',
            'username': 'john',
            'password': 'cat',
            'password2': 'cat'
        })
        data = response.get_data(as_text=True)
        self.assertEqual(response.status_code, 200)


class AdminTestCase(BaseTestCase):

    def test_new_post(self):
        response = self.client.get(url_for('seller_add'))
        data = response.get_data(as_text=True)
        self.assertIn('Product Add', data)

        # open the web correctly
        response = self.client.post(url_for('seller_add'), data=dict(
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        # self.assertIn('Add successfully', data)
        self.assertEqual(response.status_code, 200)

        # test_new_post_without_title
        # 测试表单验证
        response = self.client.get(url_for('seller_add'))
        data = response.get_data(as_text=True)
        self.assertIn('Product Add', data)
        # open the web correctly
        response = self.client.post(url_for('seller_add'), data=dict(
            title=''
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        print(data)
        self.assertIn('This field is required.', data)
        self.assertEqual(response.status_code, 200)



    #
    #     response = self.client.post(url_for('seller_edit', id=30), data=dict(
    #         image_file="2.jpg"
    #     ), follow_redirects=True)
    #     data = response.get_data(as_text=True)
    #     self.assertIn('Product Edit', data)
    #     self.assertEqual(response.status_code, 500)

    def test_delete_post(self):
        response = self.client.post(url_for('seller_delete', id=30), data=dict(
            id=30
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertEqual(response.status_code, 200)


class UserTestCase(BaseTestCase):
    def login(self):
        self.client.post('/login', data=dict(
            username='test',
            password='123'
        ), follow_redirects=True)

    def test_add_cart(self):
        response = self.client.get(url_for('product', product_id=30))
        data = response.get_data(as_text=True)
        self.assertIn('Product', data)

        response = self.client.post(url_for('product', product_id=30))
        data = response.get_data(as_text=True)
        self.assertEqual(response.status_code, 302)


# db test
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
        if user:
            exists = bcrypt.check_password_hash(user.password, password)
        print("user: ", user)

        self.assertTrue(exists)

    def test_product_exists(self):
        product = Product(title='test', price=120, description='for test', image_file='1.jpg', category_id=1,
                          seller_id=3)
        db.session.add(product)
        db.session.commit()
        product_test = Product.query.filter_by(title='test').first()
        self.assertIsNotNone(product_test)

    # def test_cart_all(self):
    #     cart_all = Cart.query.all()
    #     self.assertEqual(cart_all)

    def test_product_first(self):
        product = Product.query.filter().first()
        print("product: ", product)
        self.assertTrue(product != None)
        # self.assertEqual(product.users)

    def test_add_comment(self):
        product = Product.query.filter().first()
        user = User.query.filter().first()
        comment = Comment(product_id=product.id, user_id=user.id, content="")
        db.session.add(comment)
        db.session.commit()
        self.assertTrue(comment != 0)
