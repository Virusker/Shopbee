from app import app, db
from models import User, Category, Product, Order, \
                    Cart, OrderDetail, UserDetail,\
                    Payment, Delivery
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import func
# user
def create_user(username, email, password):
    _password = generate_password_hash(password)
    user = User(name=username.strip(),
                email=email.strip(),
                password=_password,
                role=1
                )
    db.session.add(user)
    db.session.commit()
    return user
def change_password(user_id, password):
    user = User.query.get(user_id)
    user.password = generate_password_hash(password)
    db.session.merge(user)
    db.session.commit()
def update_user(user_id, name, email, phone):
    user = User.query.get(user_id)
    user.name = name
    user.email = email
    user.phone = phone
    db.session.merge(user)
    db.session.commit()
def check_user(email, password):
    user = User.query.filter_by(email=email).first()
    if user and check_password_hash(user.password, password):
        return user
    return None
def get_user_by_id(user_id):
    return User.query.get(user_id)

# user_detail
def create_user_detail(user_id):
    user_detail = UserDetail(user_id=user_id)
    db.session.add(user_detail)
    db.session.commit()

def add_user_detail(user_id, address, district, city):
    user_detail = UserDetail(user_id=user_id,
                             address=address,
                             district=district,
                             city=city)
    db.session.add(user_detail)
    db.session.commit()
def get_user_detail_by_user_id(user_id):
    return UserDetail.query.filter_by(user_id=user_id).first()

def update_user_detail(user_id, address, district, city):
    user_detail = UserDetail.query.filter_by(user_id=user_id).first()
    if not user_detail:
        add_user_detail(user_id, address, district, city)
        return
    user_detail.address = address
    user_detail.district = district
    user_detail.city = city
    db.session.merge(user_detail)
    db.session.commit()

# category
def get_all_categories():
    return Category.query.all()
def get_category_by_id(category_id):
    return Category.query.get(category_id)
def delete_category_by_id(category_id):
    category = Category.query.get(category_id)
    db.session.delete(category)
    db.session.commit()
def add_category(name):
    category = Category(name=name)
    db.session.add(category)
    db.session.commit()
def edit_category(category):
    db.session.merge(category)
    db.session.commit()
# product
def get_products(category_id=None, keyword=None,sort_by=None,page=1):
    query = Product.query.filter_by(active=True)
    if category_id:
        query = query.filter_by(category_id=category_id)
    if keyword:
        keyword = keyword.lower()
        query = query.filter(func.lower(Product.name).contains(keyword))
    if sort_by == 'asc':
        query = query.order_by(Product.price.asc())
    elif sort_by == 'desc':
        query = query.order_by(Product.price.desc())
    elif sort_by == 'new':
        query = query.order_by(Product.created_at.desc())
    elif sort_by == 'hot':
        # sort by total quantity of product in order_detail
        query = query.outerjoin(OrderDetail).group_by(Product.id).order_by(func.coalesce(func.sum(OrderDetail.quantity), 0).desc())
        # query = query.join(OrderDetail).group_by(Product.id).order_by(func.sum(OrderDetail.quantity).desc())

    page_size = app.config['PAGE_SIZE']
    start = (page - 1) * page_size
    query = query.offset(start).limit(page_size)

    products = query.all()

    return products

def get_total_products(category_id=None, keyword=None):
    query = Product.query.filter_by(active=True)
    if category_id:
        query = query.filter_by(category_id=category_id)
    if keyword:
        keyword = keyword.lower()
        query = query.filter(func.lower(Product.name).contains(keyword))
    return query.count()

def get_all_products():
    return Product.query.all()
def get_products_by_category(category_id):
    return Product.query.filter_by(category_id=category_id).all()
def find_product_by_keyword(keyword):
    keyword = keyword.lower()
    return Product.query.filter(func.lower(Product.name).contains(keyword)).all()                       
    #    Product.name.contains(keyword)).all()
def get_product_by_id(product_id):
    return Product.query.get(product_id)
# product join order_detail get top 4
def get_product_hot(quantity=4):
    return db.session.query(Product,
                            db.func.sum(OrderDetail.quantity
                                        ).label('total')
                            ).join(OrderDetail
                                   ).group_by(Product.id
                                            ).order_by(db.desc('total')
                                                       ).limit(quantity).all()

def product_stats(kw=None, from_date=None, to_date=None):
    query = db.session.query(
        Product,
        db.func.sum(OrderDetail.quantity * Product.price)
    ).join(OrderDetail).group_by(Product.id)
    
    if kw:
        query = query.filter(Product.name.contains(kw))
    if from_date:
        query = query.filter(OrderDetail.created_at >= from_date)
    if to_date:
        query = query.filter(OrderDetail.created_at <= to_date)
    
    return query.all()


def delete_product_by_id(product_id):
    product = Product.query.get(product_id)
    db.session.delete(product)
    db.session.commit()
def add_product(name, description, price, category_id, avatar):
    product = Product(name=name,
                      description=description,
                      price=price,
                      category_id=category_id,
                      avatar=avatar)
    db.session.add(product)
    db.session.commit()
def edit_product(product):
    db.session.merge(product)
    db.session.commit()
# cart
def add_cart(user_id, product_id, quantity):
    cart = Cart.query.filter_by(user_id=user_id, product_id=product_id).first()
    if cart:
        cart.quantity += int(quantity)
        cart.total += int(quantity) * cart.product.price
        db.session.merge(cart)
        db.session.commit()
        return
    cart = Cart(user_id=user_id,
                product_id=product_id,
                quantity=quantity,
                total= int(quantity) * Product.query.get(product_id).price
                )
    db.session.add(cart)
    db.session.commit()
def get_cart_by_user_id(user_id):
    return Cart.query.filter_by(user_id=user_id).all()
def delete_cart_by_id(cart_id):
    cart = Cart.query.get(cart_id)
    db.session.delete(cart)
    db.session.commit()
def update_cart(cart_id, quantity, total):
    cart = Cart.query.get(cart_id)
    cart.quantity = quantity
    cart.total = total
    
    db.session.merge(cart)
    db.session.commit()
# order
def add_order(user_id, total):
    order = Order(user_id=user_id, total=total)
    db.session.add(order)
    db.session.commit()
    return order

# order_detail
def add_order_detail(order_id, product_id, quantity, total):
    order_detail = OrderDetail(order_id=order_id,
                               product_id=product_id,
                               quantity=quantity,
                               total=total)
    db.session.add(order_detail)
    db.session.commit()
def get_order_detail_by_order_id(order_id):
    return OrderDetail.query.filter_by(order_id=order_id).all()

# Payment
def get_payment(payment_id):
    return Payment(payment_id).name
# Delivery
def get_delivery(delivery_id):
    return Delivery(delivery_id).name
if __name__ == '__main__':
    with app.app_context():
        # db.create_all()
        print(product_stats())
        # products = get_products(keyword='Mi')
        # print(products)
        