import random
from email.message import Message

from flask import redirect, flash, render_template, url_for, request, session, jsonify
from apps.forms import RegistrationForm, LoginForm, InforForm, UserForm, SellerForm, ProductForm
from apps import bcrypt, photos
from apps.models import *
from flask_login import current_user, login_user, login_required, logout_user


# from chatbot import bot

@app.route("/", methods=['GET', 'POST', 'PUT'])
@app.route("/home")
def home():
    app.logger.info("Enter the home page")
    # Set the session expiry time
    session.permanent = True
    return render_template('home.html')


@app.route("/register", methods=['GET', 'POST'])
def register():
    global user_type
    app.logger.info("User try to sign up")
    if current_user.is_authenticated:
        redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        app.logger.info("USer submit the information to sign up")
        passwords = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        usernames = form.username.data
        emails = form.email.data
        type_user = request.form.get("type_select")
        if type_user == "Seller":
            user_type = 2
        elif type_user == "Consumer":
            user_type = 3
        users = User()
        users.username = usernames
        users.email = emails
        users.password = passwords
        users.user_type = user_type
        db.session.add(users)
        db.session.commit()
        app.logger.info("Registration successful")
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
            session['email'] = form.email.data
            flash(f'Login successfully!', 'success')
            if user.user_type == 1 or user.user_type == 2:
                app.logger.info("%s login", current_user.username)
                return redirect(url_for('seller_home'))
            else:
                app.logger.info("%s login", current_user.username)
                return redirect(url_for('home'))
        else:
            app.logger.warning("%s login failed", current_user.username)
            flash(f'Please check the information!', 'danger')
        return render_template('login.html', form=form, title='Login')
    return render_template('login.html', form=form, title='Login')


@app.route('/sort/<string:category_name>', methods=['POST', 'GET'])
def soft_products(category_name):
    page = request.args.get('page', 1, type=int)
    if 'sort' in session and request.form.get("sort") == None:
        sort = session['sort']
    else:
        sort = int(request.form.get("sort"))
        session['sort'] = sort
    sorts = {0: Product.title, 1: Product.title, 2: Product.price}
    categories = Category.query.all()
    if category_name != 'All':
        category = Category.query.filter_by(name=category_name).first_or_404()
        products = Product.query.filter_by(type=category).order_by(sorts[sort].desc()).paginate(page=page, per_page=9)
    else:
        category = categories
        products = Product.query.order_by(sorts[sort].desc()).paginate(page=page, per_page=9)
    return render_template('sort.html', title='Categories', products=products, categories=categories, category=category,
                           category_name=category_name)


@app.route('/categories/<string:category_name>')
def category(category_name):
    app.logger.info("category items")
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
    if product:
        app.logger.info("Successfully query %s", product.title)
    else:
        app.logger.warning("Query %s failed", product.title)
    comments = Comment.query.filter_by(product=product).order_by(Comment.date_posted.desc())
    if comments:
        app.logger.info("Successfully query")
    else:
        app.logger.warning("Query failed")
    if request.method == 'POST':
        if current_user.is_authenticated:
            app.logger.info("%s add products", current_user.username)
            quantity = int(request.form.get('quantity'))
            product_incart = Cart.query.filter_by(product_id=product.id, user_id=current_user.id).first()
            if product_incart:
                product_incart.quantity += quantity
                product_incart.item_total_price = product.price * product_incart.quantity
                db.session.commit()
            else:
                t = Cart(title=product.title, price=product.price, image_file=product.image_file, quantity=quantity,
                         item_total_price=product.price * quantity, user_id=current_user.id, product_id=product.id)
                app.logger.info("Successfully added items to cart table")
                db.session.add(t)
                db.session.commit()
            session['quantity'] = 0
            all_cart = Cart.query.all()
            for i in all_cart:
                session['quantity'] += 1
            app.logger.info("%s add product to shopping cart successfully", current_user.username)
            flash(f'Adding to shopping cart successfully!', 'success')
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
    if 'content_error' in session:
        app.logger.warning("content error ")
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
        app.logger.info("%s add product into Favourite folder", current_user.username)
        db.session.commit()
        return redirect(url_for('product', product_id=product_id))
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
    app.logger.info("%s successfully added new comment to comment table", current_user.username)
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
            app.logger.info("Successfully added information to info table")
            cart_items = Cart.query.all()
            items = []
            for i in cart_items:
                # 1: done 2: on the way(return, receive) 3: agree/returning a product 4: reject(apply again )
                product = Product.query.filter_by(id=i.product_id).first()

                c1 = CartItem(product_id=product.id, quantity=i.quantity, infor_id=infor.id, user_id=current_user.id,
                              seller_id=product.seller_id)
                items.append(c1)
            db.session.add_all(items)
            app.logger.info("Successfully added product to cart_item table")
            # db.session.add(c1)
            db.session.commit()
            flash(f'You ordered successfully!', 'success')
            for i in cart_items:
                db.session.delete(i)
                db.session.commit()
            app.logger.info("Successfully delete product from cart table")
            return redirect('/home')
        else:
            flash('Please log in to access this page.')
            return redirect(url_for('login'))

    return render_template('checkout.html', title='Check Out', form=form, total=total, subtotal=total_price,
                           shipping=shipping)


@app.route('/order', methods=['POST', 'GET'])
def order():
    history_order = {}
    if current_user.is_authenticated:
        order_items = CartItem.query.filter_by(user_id=current_user.id).all()
        for i in order_items:
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
            history_order[product.title].append(i.id)
        return render_template('orders.html', history_order=history_order)
    else:
        flash('Please log in to access this page.')
        return redirect(url_for('login'))


@app.route('/cart/remove/<int:product_id>', methods=['POST'])
def remove_from_cart(product_id):
    cart_item = Cart.query.filter_by(id=product_id).first()
    if cart_item:
        db.session.delete(cart_item)
        db.session.commit()
    app.logger.info("Successfully delete all product from cart table")
    return redirect(url_for('cart'))
    # return jsonify(code=0, message='OK')


@app.route('/cart/deleteall', methods=['POST'])
def delete_all():
    t = Cart.query.all()
    for i in t:
        db.session.delete(i)
        db.session.commit()
    return redirect(url_for('cart'))


@app.route('/cart/update/<int:product_id>', methods=['POST'])
def update_cart(product_id):
    quantity = int(request.form.get('update_num'))
    cart_item = Cart.query.filter_by(product_id=product_id).first()
    cart_item.quantity = quantity
    db.session.commit()
    return redirect(url_for('cart'))


@app.route('/logout')
def logout():
    logout_user()
    app.logger.info("logout")

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
        app.logger.info("Successful modification of database information")
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
    product = Product.query.get(id)
    cartitems = CartItem.query.filter_by(product_id=id).all()
    for cartitem in cartitems:
        db.session.delete(cartitem)
    db.session.delete(product)
    db.session.commit()
    app.logger.info("seller delete the product")
    return jsonify(code=0, message="OK")


@app.route('/seller_edit/<int:id>', methods=['GET', 'POST'])
def seller_edit(id):
    product = Product.query.get(id)
    if not product:
        return render_template(url_for('seller_home'))
    form = SellerForm(obj=product)
    if form.validate_on_submit():
        product.title = form.title.data
        product.price = form.price.data
        product.description = form.description.data
        # product.image_file = form.image_file.data
        # product.image_file = photos.save(form.photo.data)
        product.image_file = photos.save(form.photo.data)
        # file_url = photos.url(product.image_file)
        # file_url = photos.url(filename)
        app.logger.info("seller edit the product")
        app.logger.info("Successful modification of database information")

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
        t.seller_id = current_user.id
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
        app.logger.info("seller add the product")

        flash('Add successfully', 'success')
        return redirect('/seller_home')
    return render_template('seller_add.html', product=product, form=form)


@app.route('/confirmation/<int:id>', methods=['GET', 'POST'])
def confirmation(id):
    cart_item = CartItem.query.get(id)
    cart_item.status = 1
    db.session.commit()
    return redirect('/order')


# 1: done 2: on the way(return, receive) 3:waiting 4. agree/returning a product 5:applying
@app.route('/return_item/<int:id>', methods=['GET', 'POST'])
def return_item(id):
    cart_item = CartItem.query.get(id)
    cart_item.status = 5
    db.session.commit()
    return redirect('/order')


@app.route('/seller_order', methods=['GET', 'POST'])
def seller_order():
    product_items = {}
    if current_user.is_authenticated:
        cart_items = CartItem.query.filter_by(seller_id=current_user.id)
        for i in cart_items:
            product = Product.query.filter_by(id=i.product_id).first()
            infor = Infor.query.filter_by(id=i.infor_id).first()
            product_items[product.title] = []
            product_items[product.title].append(product.price)
            product_items[product.title].append(product.image_file)
            product_items[product.title].append(i.quantity)
            product_items[product.title].append(infor.name)
            product_items[product.title].append(infor.phone)
            product_items[product.title].append(infor.country)
            product_items[product.title].append(infor.address)
            product_items[product.title].append(i.id)
            # product_items[product.title].append(infor.cartitems.id)
            product_items[product.title].append(i.status)
        return render_template('seller_order.html', product_items=product_items)
    else:
        flash('Please log in to access this page.')
        return redirect(url_for('login'))


@app.route('/agree/<int:id>', methods=['GET', 'POST'])
def agree(id):
    cart_item = CartItem.query.get(id)
    cart_item.status = 3
    app.logger.info("Agree to user return")

    db.session.commit()
    return redirect('/seller_order')


@app.route('/reject/<int:id>', methods=['GET', 'POST'])
def reject(id):
    cart_item = CartItem.query.get(id)
    cart_item.status = 4
    db.session.commit()
    app.logger.info("Refusal to return a product to a user")
    return redirect('/seller_order')



