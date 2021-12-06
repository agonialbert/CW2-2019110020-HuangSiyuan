import random

from flask import redirect, flash, render_template, url_for, request, session, jsonify
from apps.forms import RegistrationForm, LoginForm, InforForm, UserForm, SellerForm, ProductForm
from apps import bcrypt, app, photos
from apps.models import *
from flask_login import current_user, login_user, login_required, logout_user


# from chatbot import bot

@app.route("/", methods=['GET', 'POST', 'PUT'])
@app.route("/home")
def home():
    app.logger.info("home info")
    # Set the session expiry time
    session.permanent = True
    return render_template('home.html')


@app.route("/about")
def about():
    return render_template('about.html')


@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        passwords = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        usernames = form.username.data
        emails = form.email.data
        type_user = request.form.get("type_select")
        if type_user == "Seller":
            usertype = 2
        elif type_user == "Consumer":
            usertype = 3
        # type_gender = request.form.get("gender")
        # print(type_gender)
        users = User(username=usernames, email=emails, password=passwords, user_type=usertype)
        db.session.add(users)
        db.session.commit()
        flash(f'Your account have been created!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form, title='Register')


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            flash(f'Login succesfully!', 'success')
            if user.user_type == 1 or user.user_type == 2:
                return redirect(url_for('seller_home'))
            else:
                return redirect(url_for('home'))
        else:
            flash(f'Please check the information!', 'danger')
    return render_template('login.html', form=form, title='Login')


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    session['firstname'] = request.form.get('firstname')
    session['lastname'] = request.form.get('lastname')
    session['email'] = request.form.get('email')
    session['subject'] = request.form.get('subject')
    session['message'] = request.form.get('message')
    print(session['firstname'], session['lastname'], session['email'], session['subject'], session['message'])
    if session['firstname'] != None:
        flash(f'Message sent!', 'success')
    return render_template('contact.html', tilte='Contact')


@app.route('/sort/<string:category_name>', methods=['POST', 'GET'])
def soft_products(category_name):
    page = request.args.get('page', 1, type=int)
    print(request.form.get("sort"))
    if 'sort' in session and request.form.get("sort") == None:
        sort = session['sort']
    else:
        sort = int(request.form.get("sort"))
        session['sort'] = sort
    print(sort)
    sorts = {0: Product.title, 1: Product.title, 2: Product.price}
    categories = Category.query.all()
    if category_name != 'All':
        category = Category.query.filter_by(name=category_name).first_or_404()
        products = Product.query.filter_by(type=category).order_by(sorts[sort].desc()).paginate(page=page, per_page=8)
    else:
        category = None
        products = Product.query.order_by(sorts[sort].desc()).paginate(page=page, per_page=8)
    return render_template('sort.html', title='Categories', products=products, categories=categories, category=category,
                           category_name=category_name)


@app.route('/categories/<string:category_name>')
def category(category_name):
    page = request.args.get('page', 1, type=int)
    categories = Category.query.all()
    if category_name == 'All':
        category = None
        products = Product.query.order_by(Product.title.desc()).paginate(page=page, per_page=9)
    else:
        category = Category.query.filter_by(name=category_name).first_or_404()
        products = Product.query.filter_by(type=category).paginate(page=page, per_page=9)
    return render_template('category.html', title='Categories', category=category, products=products,
                           categories=categories, category_name=category_name)


@app.route('/product/<int:product_id>', methods=['POST', 'GET'])
def product(product_id):
    product = Product.query.get_or_404(product_id)
    comments = Comment.query.filter_by(product=product).order_by(Comment.date_posted.desc())
    if request.method == 'POST':
        if current_user.is_authenticated:
            quantity = int(request.form.get('quantity'))
            product_incart = Cart.query.filter_by(title=product.title, user_id=current_user.id).first()
            if product_incart:
                product_incart.quantity += quantity
                product_incart.item_total_price = product.price * product_incart.quantity
                db.session.commit()
            else:
                t = Cart(title=product.title, price=product.price, image_file=product.image_file, quantity=quantity,
                         item_total_price=product.price * quantity, user_id=current_user.id)
                db.session.add(t)
                db.session.commit()
            session['quantity'] = 0
            all_cart = Cart.query.all()
            for i in all_cart:
                session['quantity'] += 1
            flash(f'Adding to shopping cart succesfully!', 'success')
        else:
            flash('Please log in to access this page.')
            return redirect(url_for('login'))

    product_typeid = product.category_id
    category_item = Product.query.filter_by(category_id=product_typeid).all()
    # category_itemsid=[]
    # category_items=[]
    # for i in category_item:
    #     category_itemsid.append(i.id)
    random_itemid = random.sample(category_item, 4)
    print(random_itemid)
    if 'content_error' in session:
        content_error = session['content_error']
    else:
        content_error = None
    return render_template('product.html', title='Product', product=product, random_itemid=random_itemid,
                           comments=comments, content_error=content_error)


@app.route('/product_collect/<int:product_id>', methods=['POST', 'GET'])
def product_collect(product_id):
    if current_user.is_authenticated:
        product_item = Product.query.get(product_id)
        user_item = User.query.get(current_user.id)
        user_item.product.append(product_item)

        db.session.commit()
        return redirect(url_for('home'))
    else:
        flash('Please log in to access this page.')
        return redirect(url_for('login'))

    # quantity = int(request.form.get('quantity'))
    # product_incart = Cart.query.filter_by(title=product.title).first()
    # if product_incart:
    #     product_incart.quantity += quantity
    #     product_incart.item_total_price = product.price*product_incart.quantity
    #     db.session.commit()
    # else:
    #     t = Cart(title=product.title, price=product.price, image_file=product.image_file, quantity=quantity,
    #            item_total_price=product.price*quantity)
    #     db.session.add(t)
    #     db.session.commit()
    # session['quantity'] = 0
    # all_cart = Cart.query.all()
    # for i in all_cart:
    #     session['quantity'] += 1
    # flash(f'Adding to shopping cart succesfully!', 'success')


@app.route('/product/<int:product_id>/new_comment', methods=['POST', 'GET'])
@login_required
def new_comment(product_id):
    content = request.args.get('content')
    product = Product.query.get_or_404(product_id)
    author = current_user
    # content_chatbot = str(bot.get_response(content))
    comment = Comment(content=content, author=author, product=product)
    db.session.add(comment)
    db.session.commit()
    flash('Adding new comment successfully!')
    return redirect(url_for('product', product_id=product.id))


@app.route('/cart', methods=['POST', 'GET'])
def cart():
    if current_user.is_authenticated:
        total_price = 0
        session['quantity'] = 0
        cart_items = Cart.query.filter_by(user_id=current_user.id).all()
        for i in cart_items:
            total_price += i.quantity * i.price
            session['quantity'] += 1
        # session['order'] = order
        shipping = 10
        shipping_free = 0
        total = total_price + shipping
        session['shipping'] = shipping
        session['total_price'] = total_price
        session['total'] = total
        return render_template('cart.html', title='Cart', total=total, total_price=total_price, shipping=shipping,
                               shipping_free=shipping_free, cart_items=cart_items)
    else:
        flash('Please log in to access this page.')
        return redirect(url_for('login'))


@app.route('/collect', methods=['POST', 'GET'])
def collect():
    if current_user.is_authenticated:
        products = Product.query.filter(Product.users.any(User.id == current_user.id))
        # products = current_user.product.all()
        return render_template('collect.html', products=products)
    else:
        flash('Please log in to access this page.')
        return redirect(url_for('login'))


@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    total = session['total']
    total_price = session['total_price']
    shipping = session['shipping']
    form = InforForm()
    if form.validate_on_submit():
        if current_user.is_authenticated:
            country = request.form.get('country_select')
            infor = Infor(name=form.name.data, address=form.address.data, country=country, city=form.city.data,
                          phone=form.phone.data)
            db.session.add(infor)
            db.session.commit()
            cart_items = Cart.query.all()
            items = []
            for i in cart_items:
                # 1: done 2: on the way(return, receive) 3: agree/returning a product 4: reject(apply again )
                product = Product.query.filter_by(title=i.title).first()
                c1 = CartItem(product_id=product.id, quantity=i.quantity, infor_id=infor.id, user_id=current_user.id)
                items.append(c1)
            db.session.add_all(items)
            # db.session.add(c1)
            db.session.commit()
            flash(f'You ordered successfully!', 'success')
            for i in cart_items:
                db.session.delete(i)
                db.session.commit()
            return redirect('/home')
        else:
            flash('Please log in to access this page.')
            return redirect(url_for('login'))

    return render_template('checkout.html', title='Check Out', form=form, total=total, subtotal=total_price,
                           shipping=shipping)


@app.route('/order', methods=['POST', 'GET'])
def order():
    history_order = {}
    order_items = CartItem.query.filter_by(user_id=current_user.id).all()
    if current_user.is_authenticated:
        for i in order_items:
            # print(i.product_id.name)
            print('*******************')
            product = Product.query.filter_by(id=i.product_id).first()
            infor = Infor.query.filter_by(id=i.infor_id).first()
            history_order[product.title] = []
            history_order[product.title].append(product.price * i.quantity)
            history_order[product.title].append(product.image_file)
            history_order[product.title].append(i.quantity)
            history_order[product.title].append(infor.name)
            history_order[product.title].append(infor.phone)
            history_order[product.title].append(infor.order_date.strftime('%b %d %Y'))
            history_order[product.title].append(infor.address)
            history_order[product.title].append(infor.city)
            history_order[product.title].append(infor.country)
            history_order[product.title].append(i.status)
            history_order[product.title].append(product.id)
        print(history_order)
        return render_template('orders.html', history_order=history_order)
    else:
        flash('Please log in to access this page.')
        return redirect(url_for('login'))


@app.route('/cart/remove/<string:product_title>', methods=['POST'])
def remove_from_cart(product_title):
    cart_item = Cart.query.filter_by(title=product_title).first()
    if cart_item:
        db.session.delete(cart_item)
        db.session.commit()
    return redirect(url_for('cart'))
    # return jsonify(code=0, message='OK')


@app.route('/cart/deleteall', methods=['POST'])
def delete_all():
    t = Cart.query.all()
    for i in t:
        db.session.delete(i)
        db.session.commit()
    return redirect(url_for('cart'))


@app.route('/cart/update', methods=['POST'])
def update_cart():
    num = request.form.get('update_num')
    p = request.form.get('update_des')
    for i in session['cart']:
        if p in i:
            i.update({p: int(num)})
    return redirect(url_for('cart'))


# @app.route('/search', methods=['POST', 'GET'])
# def search():
#     index_name = 'fashionshop'
#     doc_type = 'product'
#     query = request.form.get('query')
#     print(query)
#     query = es.search(index=index_name, body={'query': {'match': {'title': query}}})
#     found = query['hits']['total']['value']
#     products = []
#     print(query['hits']['hits'])
#     for item in query['hits']['hits']:
#         product = Product.query.filter_by(title=item['_source']['title']).first()
#         print(product)
#         products.append(product)
#     print(products)
#     return render_template('search.html', products=products, found=found)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/user', methods=['GET', 'POST'])
@login_required
def user():
    form = UserForm(obj=current_user)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        current_user.email = form.email.data
        current_user.birthday = form.birthday.data
        current_user.gender = form.gender.data
        db.session.commit()
        print('Save successfully!')
        flash(f'Your account information has updated!', 'success')
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.birthday.data = current_user.birthday
        form.gender.data = current_user.gender
    return render_template('user.html', title='User', form=form)


# seller page
@app.route('/seller_home', methods=['GET', 'POST'])
def seller_home():
    products = Product.query.filter_by(seller_id=current_user.id).all()
    # product_item = {}
    # product_data = {}
    # product_data['data'] = [].
    # for product in products:
    #     product_item['title'] = product.title
    #     product_item['price'] = product.price
    #     product_item['description'] = product.description
    #     product_data['data'].append(product_item)
    # return jsonify(product_data)
    return render_template('seller_home.html', products=products)


@app.route('/seller_delete/<int:id>', methods=['GET', 'POST'])
def seller_delete(id):
    # req_dict=request.get_json()
    # product_id = req_dict.get("product_id")
    # print(product_id)
    product = Product.query.get(id)
    cartitems = CartItem.query.filter_by(product_id=id).all()
    for cartitem in cartitems:
        db.session.delete(cartitem)
    db.session.delete(product)
    db.session.commit()
    return jsonify(code=0, message="OK")


@app.route('/seller_edit/<int:id>', methods=['GET', 'POST'])
def seller_edit(id):
    product = Product.query.get(id)
    print(product)
    if not product:
        return render_template(url_for('seller_home'))
    form = SellerForm(obj=product)
    if form.validate_on_submit():
        product.title = form.title.data
        product.price = form.price.data
        print(form.price.data)
        product.description = form.description.data
        # product.image_file = form.image_file.data
        # product.image_file = photos.save(form.photo.data)
        product.image_file = photos.save(form.photo.data)
        # file_url = photos.url(product.image_file)
        print(product.image_file)
        # file_url = photos.url(filename)
        db.session.commit()
        return redirect('/seller_home')
    return render_template('seller_edit.html', product=product, form=form)


@app.route('/seller_add', methods=['GET', 'POST'])
def seller_add():
    form = ProductForm()
    if form.validate_on_submit():
        t = Product()
        t.title = form.title.data
        t.price = form.price.data
        t.description = form.description.data
        t.image_file = photos.save(form.photo.data)
        type = request.form.get("type_select")
        if type == "Male":
            t.category_id = 1
        elif type == "Female":
            t.category_id = 2
        elif type == "Children":
            t.category_id = 3
        db.session.add(t)
        # gender = gender
        db.session.commit()
        return redirect('/seller_home')
    return render_template('seller_add.html', product=product, form=form)


@app.route('/confirmation/<int:product_id>', methods=['GET', 'POST'])
def confirmation(product_id):
    cart_item = CartItem.query.filter_by(product_id=product_id).all()
    cart_item.status = 1
    return redirect('/order')


# 1: done 2: on the way(return, receive) 3:waiting 4. agree/returning a product 4: reject(apply again )
@app.route('/return_item/<int:product_id>', methods=['GET', 'POST'])
def return_item(product_id):
    cart_item = CartItem.query.filter_by(product_id=product_id).all()
    cart_item.status = 3
    return redirect('/order')


@app.route('/agree/<int:product_id>', methods=['GET', 'POST'])
def agree(product_id):
    cart_item = CartItem.query.filter_by(product_id=product_id).all()
    cart_item.status = 4
    return redirect('/seller_return')


@app.route('/reject/<int:product_id>', methods=['GET', 'POST'])
def reject(product_id):
    cart_item = CartItem.query.filter_by(product_id=product_id).all()
    cart_item.status = 5
    return redirect('/seller_return')





