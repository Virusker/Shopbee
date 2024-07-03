from flask import Flask, request, render_template, redirect, url_for, jsonify,session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
import os
import math
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__, template_folder='../templates', static_folder='../static')

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['PAGE_SIZE'] = 8
login_manager = LoginManager(app)
db = SQLAlchemy(app)

from utils import *

@login_manager.user_loader
def load_user(user_id):
    return get_user_by_id(user_id)
@login_manager.unauthorized_handler
def unauthorized():
    return redirect(url_for('login'))
@app.route('/')
def index():
    list_products = get_products(sort_by='new')
    
    hot_products = get_products(sort_by='hot')
    
    return render_template('index.html', products=list_products, hot_products=hot_products)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = check_user(email, password)
        if user:
            login_user(user)
            return redirect(url_for('index'))
        else:
            err = 'Invalid email or password'
            return render_template('login.html', error=err)
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['name']
        email = request.form['email']
        password = request.form['password']
        user = create_user(username, email, password)
        create_user_detail(user.id)

        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/change_password', methods=['POST'])
def password_change():
    old_password = request.form['old_password']
    new_password = request.form['new_password']
    user = check_user(current_user.email, old_password)
    if not user:
        return jsonify({'status': 'error', 'message': 'Mật khẩu cũ không đúng'})
    change_password(current_user.id, new_password)
    logout_user()
    return jsonify({'status': 'success' ,'message': 'Thay đổi mật khẩu thành công'})

@app.route('/products')
def products():
    c_id = request.args.get('cid')
    kw = request.args.get('kw')
    sort_by = request.args.get('s')
    page = request.args.get('page',1,type=int)
    products = get_products(category_id=c_id, keyword=kw, sort_by= sort_by, page=page)
    total_products = get_total_products(category_id=c_id, keyword=kw)
    total_pages = math.ceil(total_products / app.config['PAGE_SIZE'])

    print(total_products)
    print(total_pages)
    return render_template('products.html', products=products, total_pages=total_pages, page=page)

@app.route('/product/<int:id>')
def product(id):
    product = Product.query.get(id)
    return render_template('product.html', product=product)

@app.route('/cart')
def cart():
    if current_user.is_authenticated:
        carts = get_cart_by_user_id(current_user.id)
    else:
        carts = []
        cart = session.get('cart', {})
        for key, value in cart.items():
            carts.append(value)
    print(carts)
    return render_template('cart.html', carts=carts)

@app.route('/api/add_to_cart', methods=['POST'])
def add_to_cart():
    product_id = request.form['product_id']
    product_name = request.form['product_name']
    priduct_price = request.form['product_price']
    quantity = request.form['quantity']

    if not current_user.is_authenticated:
        cart = session.get('cart', {})
        if product_id in cart:
            cart[product_id]['quantity'] += int(quantity)
        else:
            cart[product_id] = {
                'product_id': product_id,
                'product_name': product_name,
                'product_price': priduct_price,
                'quantity': int(quantity)
            }
            print(cart)
            session['cart'] = cart
    # cart.append({'product_id': product_id, 'quantity': quantity})
    else:
        add_cart(current_user.id, product_id, quantity)
    return jsonify({'status': 'success', 'message': 'Thêm vào giỏ hàng thành công'})

@app.route('/update_cart', methods=['POST'])
@login_required
def cart_update():
    cart_id = request.form['cart_id']
    quantity = request.form['quantity']
    total = request.form['total']

    update_cart(cart_id, quantity, total)
    return redirect(url_for('cart'))

@app.route('/remove_from_cart')
def remove_from_cart():
    id = request.args.get('id')
    delete_cart_by_id(id)
    return redirect(url_for('cart'))

@app.route('/checkout')
def checkout():
    carts = get_cart_by_user_id(current_user.id)
    total = sum([cart.total for cart in carts])
    user_detail = get_user_detail_by_user_id(current_user.id)
    return render_template('checkout.html', user_detail=user_detail,carts=carts, total=total)

@app.route('/order_confirm', methods=['POST'])
def order_confirm():
    name = request.form['name']
    email = request.form['email']
    address = request.form['address']
    district = request.form['district']
    city = request.form['city']
    phone = request.form['phone']
    note = request.form['note']
    delivery = request.form['delivery']
    payment = request.form['payment']
    
    total = request.form['total']
    o_confirm = {
        'name': name,
        'email': email,
        'address': address,
        'district': district,
        'city': city,
        'phone': phone,
        'note': note,
        'delivery': get_delivery(int(delivery)),
        'payment': get_payment(int(payment)),
        'total': int(total)
    }
    print(o_confirm)
    carts = get_cart_by_user_id(current_user.id)
    # create order
    order = add_order(current_user.id, total)
    for cart in carts:
        add_order_detail(order.id, cart.product_id, cart.quantity, cart.total)

    # # delete cart
    # for cart in carts:
    #     delete_cart_by_id(cart.id)


    return render_template('order_confirm.html',
                           order=order,
                           carts=carts,
                           o_confirm=o_confirm,
                           )


@app.route('/settings')
@login_required
def settings():
    user_detail = get_user_detail_by_user_id(current_user.id)
    activepage = request.args.get('activepage')
    if not activepage:
        activepage = 'info'
    return render_template('settings.html', user_detail=user_detail, activepage=activepage)

@app.route('/settings/update-info', methods=['POST'])
@login_required
def settings_update_info():
    name = request.form['name']
    email = request.form['email']
    phone = request.form['phone']
    update_user(current_user.id, name, email, phone)
    activepage = 'info'
    return redirect(url_for('settings',activepage=activepage))

@app.route('/settings/update-address', methods=['POST'])
@login_required
def settings_update_address():
    address = request.form['address']
    district = request.form['district']
    city = request.form['city']
    update_user_detail(current_user.id, address, district, city)
    activepage = 'address'

    return redirect(url_for('settings',activepage=activepage))


# search
@app.route('/search')
def search():
    search_term = request.args.get('q')
    sort_by = request.args.get('s')
    products = get_products(keyword=search_term, sort_by=sort_by)
    total_products = get_total_products(keyword=search_term)
    total_pages = math.ceil(total_products / app.config['PAGE_SIZE'])

    return render_template('products.html', products=products, total_pages=total_pages)

@app.route('/get_suggestions', methods=['GET'])
def get_suggestions():
    search_term = request.args.get('term')
    results = [word.name for word in get_all_products() if search_term.lower() in word.name.lower()]
    return jsonify(results=results)
# admin
@app.route('/admin/dashboard')
@login_required
def dashboard():
    if current_user.role == 0:
        return render_template('admin/dashboard.html')
    return redirect(url_for('index'))
    

@app.route('/admin/products')
@login_required
def admin_products():
    if current_user.role == 0:
        products = get_all_products()
        return render_template('admin/products.html', products=products)
    return redirect(url_for('index'))

@app.route('/admin/product/add', methods=['GET', 'POST'])
@login_required
def admin_add_product():
    if current_user.role == 0:
        if request.method == 'POST':
            name = request.form['name']
            description = request.form['description']
            price = request.form['price']
            category_id = request.form['category_id']
            avatar = request.form['avatar']
            add_product(name, description, price, category_id, avatar)
            return redirect(url_for('admin_products'))

        return render_template('admin/add_product.html')
    return redirect(url_for('index'))

@app.route('/admin/product/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def admin_edit_product(id):
    if current_user.role == 0:
        product = get_product_by_id(id)
        if request.method == 'POST':
            product.name = request.form['name']
            product.description = request.form['description']
            product.price = request.form['price']
            product.category_id = request.form['category_id']
            product.avatar = request.form['avatar']
            edit_product(product)
            return redirect(url_for('admin_products'))
        return render_template('admin/edit_product.html', product=product)
    return redirect(url_for('index'))

@app.route('/admin/product/delete/<int:id>')
@login_required
def admin_product_delete(id):
    if current_user.role == 0:
        delete_product_by_id(id)
        return redirect(url_for('admin_products'))
    return redirect(url_for('index'))

@app.route('/admin/categories')
@login_required
def admin_categories():
    if current_user.role == 0:
        categories = get_all_categories()
        return render_template('admin/categories.html', categories=categories)
    return redirect(url_for('index'))

@app.route('/admin/category/add', methods=['GET', 'POST'])
@login_required
def admin_add_category():
    if current_user.role == 0:
        if request.method == 'POST':
            name = request.form['name']
            description = request.form['description']
            category = Category(name=name, description=description)
            db.session.add(category)
            db.session.commit()
            return redirect(url_for('admin_categories'))
        return render_template('admin/add_category.html')
    
    return redirect(url_for('index'))

@app.route('/admin/category/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def admin_edit_category(id):
    if current_user.role == 0:
        category = get_category_by_id(id)
        if request.method == 'POST':
            category.name = request.form['name']
            category.description = request.form['description']
            edit_category(category)
            return redirect(url_for('admin_categories'))
        return render_template('admin/edit_category.html', category=category)
    return redirect(url_for('index'))

@app.route('/admin/category/delete/<int:id>')
@login_required
def admin_category_delete(id):
    if current_user.role == 0:
        delete_category_by_id(id)
        return redirect(url_for('admin_categories'))
    return redirect(url_for('index'))

@app.route('/admin/reports')
@login_required
def admin_reports():
    if current_user.role == 0:
        kw = request.args.get('kw')
        from_date = request.args.get('from_date')
        to_date = request.args.get('to_date')
        p_stats = product_stats(kw=kw, from_date=from_date, to_date=to_date)
        

        return render_template('admin/reports.html' , product_stats=p_stats)
    return redirect(url_for('index'))

@app.context_processor
def inject_categories():
    categories = get_all_categories()
    total_quantity_cart = 0
    if current_user.is_authenticated:
        total_quantity_cart = sum([cart.quantity for cart in get_cart_by_user_id(current_user.id)])
    else:
        total_quantity_cart = sum([cart['quantity'] for cart in session.get('cart', []).values()])
    return dict(categories=categories, total_quantity_cart=total_quantity_cart)
