from flask import render_template, abort, redirect, url_for, flash, request, current_app, jsonify, Flask
from . import main
from app.models import User, Permission, Product, Cart, CartItem, Order, Review, Dislike, Like, Role, SavedProduct, OrderItem
from .forms import ProductForm, RoleForm, OrderForm, OrderStatusForm
from ..decorators import admin_required, permission_required
from flask_login import login_required, current_user
from .. import db
from werkzeug.utils import secure_filename
import os
from flask_wtf import CSRFProtect, FlaskForm
from .forms import ReviewForm
import uuid

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
csrf = CSRFProtect(app)


def allowed_file(filename):
    """Проверяет, разрешено ли загружать файл с данным расширением."""
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@main.route('/index', methods=['GET'])
def index():
    """
    Отображает главную страницу сайта.

    Загружает все продукты из базы данных и отображает их на главной странице.
    Также передает форму для добавления отзыва в шаблон.
    """
    products = Product.query.all()
    form = ReviewForm()  # Создаем объект формы
    return render_template('main/index.html', products=products, form=form)  # Передаем форму в шаблон


@main.route('/add_product', methods=['GET', 'POST'])
@login_required
@admin_required  # Только администратор может добавлять товары
def add_product():
    """
    Добавление нового продукта.

    Обрабатывает GET и POST запросы для добавления нового продукта.
    Валидация формы, сохранение изображения и добавление информации о продукте в базу данных.
    """
    form = ProductForm()
    if form.validate_on_submit():
        product = Product(
            name=form.name.data,
            description=form.description.data,
            price=form.price.data,
            author=form.author.data  # Добавляем автора
        )
        image_file = request.files.get('image')

        if image_file and image_file.filename != '' and allowed_file(image_file.filename):
            filename = secure_filename(image_file.filename)
            unique_filename = str(uuid.uuid4()) + "_" + filename  # Генерируем уникальное имя файла
            image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
            image_file.save(image_path)
            product.image_url = unique_filename  # Сохраняем уникальное имя файла
        else:
            product.image_url = 'default_image.jpg'  # Изображение по умолчанию

        db.session.add(product)
        db.session.commit()
        flash('Товар успешно добавлен.')
        return redirect(url_for('main.admin_products'))
    return render_template('admin/add_product.html', form=form)


@main.route('/cart')
def view_cart():
    """
    Отображение содержимого корзины.

    Проверяет, аутентифицирован ли пользователь. Если нет, отображает сообщение о необходимости входа.
    Загружает все товары в корзине пользователя и вычисляет общую стоимость.
    """
    if not current_user.is_authenticated:
        return render_template('order/cart.html', cart_items=None, total=0, show_login_message=True)

    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    if not cart_items:
        flash('Ваша корзина пуста.', 'warning')
        return render_template('order/cart.html', cart_items=[], total=0)

    total = sum(item.product.price for item in cart_items)
    csrf_token = (FlaskForm()).csrf_token._value()  # Получаем CSRF-токен
    return render_template('order/cart.html', cart_items=cart_items, total=total, csrf_token=csrf_token)


@main.route('/cart_status/<int:product_id>', methods=['GET'])
@login_required
def cart_status(product_id):
    """
    Проверка наличия товара в корзине.

    Возвращает JSON-ответ с информацией о том, находится ли товар в корзине текущего пользователя.
    """
    cart_item = CartItem.query.filter_by(user_id=current_user.id, product_id=product_id).first()
    if cart_item:
        return jsonify(in_cart=True)
    else:
        return jsonify(in_cart=False)


@main.route('/toggle_cart', methods=['POST'])
@login_required
def toggle_cart():
    """
    Добавление или удаление товара из корзины.

    Обрабатывает запросы на добавление и удаление товаров из корзины, возвращая соответствующий JSON-ответ.
    """
    data = request.get_json()
    product_id = data.get('product_id')
    action = data.get('action')

    product = Product.query.get_or_404(product_id)

    if not product:
        return jsonify(success=False, message="Товар не найден")

    cart_item = CartItem.query.filter_by(user_id=current_user.id, product_id=product_id).first()

    if action == 'add':
        if cart_item:
            return jsonify(success=False, message="Товар уже в корзине")
        else:
            cart_item = CartItem(user_id=current_user.id, product_id=product_id, price=product.price)
            db.session.add(cart_item)
    elif action == 'remove':
        if cart_item:
            db.session.delete(cart_item)
        else:
            return jsonify(success=False, message="Товар не найден в корзине")
    else:
        return jsonify(success=False, message="Некорректное действие")

    db.session.commit()
    return jsonify(success=True)


@main.route('/remove_from_cart', methods=['POST'])
@login_required
def remove_from_cart():
    """
    Удаление товара из корзины.

    Обрабатывает запросы на удаление товаров из корзины, возвращая соответствующий JSON-ответ.
    """
    data = request.get_json()
    product_id = data.get('product_id')

    cart_item = CartItem.query.filter_by(user_id=current_user.id, product_id=product_id).first()
    if cart_item:
        db.session.delete(cart_item)
        db.session.commit()
        return jsonify(success=True)
    else:
        return jsonify(success=False, message="Товар не найден в корзине")


@main.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    """
    Оформление заказа.

    Обрабатывает GET и POST запросы для оформления заказа. Загружает товары из корзины пользователя,
    валидирует форму заказа, сохраняет заказ и очищает корзину.
    """
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()

    if not cart_items:
        flash('Ваша корзина пуста. Пожалуйста, добавьте товары в корзину перед оформлением заказа.', 'warning')
        return redirect(url_for('main.view_cart'))

    form = OrderForm()

    if form.validate_on_submit():
        order = Order(
            user_id=current_user.id,
            name=form.name.data,
            phone=form.phone.data,
            address=form.address.data,
            comment=form.comment.data
        )
        db.session.add(order)
        db.session.commit()

        for item in cart_items:
            order_item = OrderItem(
                order_id=order.id,
                product_id=item.product_id,
                price=item.product.price
            )
            db.session.add(order_item)

        db.session.commit()

        for item in cart_items:
            db.session.delete(item)
        db.session.commit()

        return redirect(url_for('main.view_cart', order_success=True))

    return render_template('order/checkout.html', form=form, cart_items=cart_items)


@main.route('/update_cart', methods=['POST'])
@login_required
def update_cart():
    """
    Обновление количества товара в корзине.

    Обрабатывает запросы на обновление количества товаров в корзине, возвращая соответствующий JSON-ответ.
    """
    data = request.get_json()
    product_id = data.get('product_id')
    quantity = int(data.get('quantity'))

    product = Product.query.get_or_404(product_id)
    if not product:
        return jsonify(success=False, message="Товар не найден")

    cart_item = CartItem.query.filter_by(user_id=current_user.id, product_id=product_id).first()
    if not cart_item:
        return jsonify(success=False, message="Товар не найден в корзине")

    if product.quantity < quantity:
        return jsonify(success=False, message="Недостаточно товара в наличии")

    cart_item.quantity = quantity
    db.session.commit()
    return jsonify(success=True)


@main.route('/product/<int:product_id>')
def product(product_id):
    """
    Отображение страницы продукта.

    Загружает информацию о продукте, отзывы и отображает их на странице продукта. Также проверяет,
    находится ли товар в корзине или в списке сохраненных у текущего пользователя.
    """
    product = Product.query.get_or_404(product_id)
    in_cart = False
    in_saved = False
    if current_user.is_authenticated:
        cart_item = CartItem.query.filter_by(user_id=current_user.id, product_id=product_id).first()
        saved_item = SavedProduct.query.filter_by(user_id=current_user.id, product_id=product_id).first()
        if cart_item:
            in_cart = True
        if saved_item:
            in_saved = True
    reviews = Review.query.filter_by(product_id=product_id).all()
    for review in reviews:
        review.likes_count = review.likes.count()
        review.dislikes_count = review.dislikes.count()
    form = ReviewForm()
    return render_template('main/product.html', product=product, form=form, reviews=reviews, in_cart=in_cart, in_saved=in_saved)


@main.route('/error')
def test_error():
    """
    Тестовый маршрут для проверки обработки ошибок.

    Принудительно вызывает ошибку 404 для проверки обработки ошибок в приложении.
    """
    abort(404)


@main.route('/admin')
@login_required
@admin_required
def for_admin():
    """
    Отображение панели администратора.

    Загружает шаблон панели администратора для текущего пользователя.
    """
    return render_template('admin/admin.html')


@main.route('/moderator')
@login_required
@permission_required(Permission.MODERATE)
def for_moderator():
    """
    Отображение панели модератора.

    Загружает шаблон панели модератора для текущего пользователя с правами модератора.
    """
    return render_template('moderator/moderator.html')


@main.route('/moderator/orders')
@login_required
@permission_required(Permission.MODERATE)
def moderator_orders():
    """
    Отображение всех заказов для модератора.

    Загружает все заказы и отображает их в панели модератора.
    """
    orders = Order.query.all()
    form = OrderStatusForm()
    for order in orders:
        form.status.data = order.status  # Инициализация формы текущим статусом заказа
    return render_template('moderator/moderator_orders.html', orders=orders, form=form)


@main.route('/moderator/orders/delete/<int:order_id>', methods=['POST'])
@login_required
@permission_required(Permission.MODERATE)
def delete_order(order_id):
    """
    Удаление заказа модератором.

    Удаляет заказ и все связанные с ним элементы из базы данных.
    """
    order = Order.query.get_or_404(order_id)
    for item in order.items:
        db.session.delete(item)
    db.session.delete(order)
    db.session.commit()
    flash('Заказ успешно удален', 'success')
    return redirect(url_for('main.moderator_orders'))


@main.route('/moderator/orders/update_status/<int:order_id>', methods=['POST'])
@login_required
@permission_required(Permission.MODERATE)
def update_order_status(order_id):
    """
    Обновление статуса заказа модератором.

    Обрабатывает POST-запросы на обновление статуса заказа и сохраняет изменения в базе данных.
    """
    order = Order.query.get_or_404(order_id)
    form = OrderStatusForm()
    if form.validate_on_submit():
        order.status = form.status.data
        db.session.commit()
        flash('Статус заказа обновлен', 'success')
    else:
        flash('Произошла ошибка при обновлении статуса заказа', 'danger')
    return redirect(url_for('main.moderator_orders'))


@main.route('/moderator/comments')
@login_required
@permission_required(Permission.MODERATE)
def moderator_comments():
    """
    Отображение всех комментариев для модератора.

    Загружает и отображает все комментарии в панели модератора.
    """
    comments = Review.query.order_by(Review.timestamp.desc()).all()
    return render_template('moderator/moderator_comments.html', comments=comments)


@main.route('/comment/<int:comment_id>/delete', methods=['POST'])
@login_required
@permission_required(Permission.MODERATE)
def delete_comment(comment_id):
    """
    Удаление комментария модератором.

    Удаляет комментарий и все связанные с ним лайки и дизлайки из базы данных.
    """
    comment = Review.query.get_or_404(comment_id)
    likes = Like.query.filter_by(review_id=comment.id).all()
    dislikes = Dislike.query.filter_by(review_id=comment.id).all()

    for like in likes:
        db.session.delete(like)
    for dislike in dislikes:
        db.session.delete(dislike)

    db.session.delete(comment)
    db.session.commit()
    return jsonify(success=True)


@main.route('/secret')
@login_required
def secret():
    """
    Тестовый маршрут для проверки доступа только для авторизованных пользователей.

    Возвращает сообщение только для авторизованных пользователей.
    """
    return "Only for auth"


@main.route('/testConfirm')
def testConfirm():
    """
    Тестовый маршрут для генерации и проверки токена подтверждения пользователя.

    Генерирует токен подтверждения для первого пользователя и проверяет его.
    """
    user = User.query.filter_by().first()
    tmp = user.generate_confirmation_token()
    user.confirm(tmp)


@main.route('/user/<username>')
def user(username):
    """
    Отображение профиля пользователя.

    Загружает информацию о пользователе и отображает страницу его профиля.
    """
    user = User.query.filter_by(username=username).first_or_404()
    return render_template('main/profile.html', user=user)


@main.route('/profile')
@login_required
def profile():
    """
    Отображение профиля текущего пользователя.

    Загружает и отображает страницу профиля текущего пользователя с его сохраненными товарами.
    """
    saved_products = SavedProduct.query.filter_by(user_id=current_user.id).all()
    return render_template('main/profile.html', saved_products=[sp.product for sp in saved_products])


@main.route('/admin/products', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_products():
    """
    Управление продуктами для администратора.

    Обрабатывает GET и POST запросы для добавления и отображения всех продуктов в панели администратора.
    """
    form = ProductForm()
    if form.validate_on_submit():
        product = Product(
            name=form.name.data,
            description=form.description.data,
            price=form.price.data,
            author=form.author.data  # Добавляем автора
        )

        image_file = request.files.get('image')

        if image_file and image_file.filename != '' and allowed_file(image_file.filename):
            filename = secure_filename(image_file.filename)
            unique_filename = str(uuid.uuid4()) + "_" + filename  # Генерируем уникальное имя файла
            image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)

            try:
                image_file.save(image_path)
                product.image_url = unique_filename  # Сохраняем уникальное имя файла
                flash(f'Saved image to {image_path}', 'success')
                print(f"Saved image to {image_path}")
            except Exception as e:
                flash(f'Error saving image: {str(e)}', 'danger')
                print(f"Error saving image: {str(e)}")
                return redirect(request.url)
        else:
            product.image_url = 'default_image.jpg'  # Изображение по умолчанию

        db.session.add(product)
        db.session.commit()
        flash('Продукт успешно добавлен', 'success')
        print("Product added successfully")
        return redirect(url_for('main.admin_products'))

    else:
        print("Form validation failed")
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"Error in {field}: {error}", 'danger')
                print(f"Error in {field}: {error}")

    products = Product.query.all()
    return render_template('admin/admin_products.html', form=form, products=products)


@main.route('/admin/products/delete/<int:product_id>', methods=['POST'])
@login_required
@admin_required
def delete_product(product_id):
    """
    Удаляет товар по его ID. Доступно только для администраторов.
    """
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    flash('Товар успешно удален', 'success')
    return redirect(url_for('main.admin_products'))


@main.route('/admin/edit_product/<int:product_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_product(product_id):
    """
    Редактирование продукта администратором.

    Обрабатывает GET и POST запросы для редактирования информации о продукте и сохранения изменений в базе данных.
    """
    product = Product.query.get(product_id)
    if product:
        form = ProductForm()
        if request.method == 'POST' and form.validate_on_submit():
            product.name = form.name.data
            product.description = form.description.data
            product.price = form.price.data
            product.author = form.author.data  # Сохраняем автора

            if 'image' in request.files:
                image_file = request.files['image']
                if image_file and image_file.filename != '' and allowed_file(image_file.filename):
                    filename = secure_filename(image_file.filename)
                    unique_filename = str(uuid.uuid4()) + "_" + filename  # Генерируем уникальное имя файла
                    image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
                    image_file.save(image_path)
                    product.image_url = unique_filename  # Сохраняем уникальное имя файла

            db.session.commit()
            flash('Продукт успешно обновлен', 'success')
            return redirect(url_for('main.admin_products'))

        form.name.data = product.name
        form.description.data = product.description
        form.price.data = product.price
        form.author.data = product.author  # Заполняем поле автора текущим значением
    else:
        flash('Продукт не найден', 'danger')
    return redirect(url_for('main.admin_products'))


@main.route('/admin/users')
@login_required
@admin_required
def admin_users():
    """
    Управление пользователями для администратора.

    Загружает и отображает всех пользователей и их роли в панели администратора.
    """
    users = User.query.all()
    roles = Role.query.all()
    form = RoleForm()
    return render_template('admin/admin_users.html', users=users, roles=roles, form=form)


@main.route('/admin/change_user_role/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def change_user_role(user_id):
    """
    Изменение роли пользователя администратором.

    Обрабатывает POST-запросы на изменение роли пользователя и сохраняет изменения в базе данных.
    """
    user = User.query.get_or_404(user_id)
    form = RoleForm()
    if form.validate_on_submit():
        role_id = form.role.data
        role = Role.query.get_or_404(role_id)
        user.role = role
        db.session.commit()
        flash('Роль пользователя успешно изменена', 'success')
    else:
        flash('Ошибка при изменении роли пользователя', 'danger')
    return redirect(url_for('main.admin_users'))


@main.route('/admin/orders')
@login_required
@admin_required
def admin_orders():
    """
    Управление заказами для администратора.

    Загружает и отображает все заказы в панели администратора.
    """
    orders = Order.query.all()
    form = OrderStatusForm()
    return render_template('admin/admin_orders.html', orders=orders, form=form)


@main.route('/add_review/<int:product_id>', methods=['POST'])
@login_required
def add_review(product_id):
    """
    Добавление отзыва к продукту.

    Обрабатывает POST-запросы на добавление отзывов к продукту и сохраняет их в базе данных.
    """
    form = ReviewForm()
    existing_review = Review.query.filter_by(user_id=current_user.id, product_id=product_id).first()
    if existing_review:
        flash('Вы уже оставили комментарий на этот товар.', 'warning')
        return redirect(url_for('main.product', product_id=product_id))

    if form.validate_on_submit():
        review = Review(content=form.content.data, user_id=current_user.id, product_id=product_id)
        db.session.add(review)
        db.session.commit()
        flash('Ваш комментарий был успешно добавлен.', 'success')
    else:
        flash('Произошла ошибка при добавлении комментария.', 'danger')

    return redirect(url_for('main.product', product_id=product_id))


@main.route('/review/<int:review_id>/like', methods=['POST'])
@login_required
def like_review(review_id):
    """
    Лайк комментария.

    Обрабатывает POST-запросы на добавление и удаление лайков к комментариям.
    """
    review = Review.query.get_or_404(review_id)
    like = Like.query.filter_by(user_id=current_user.id, review_id=review_id).first()
    dislike = Dislike.query.filter_by(user_id=current_user.id, review_id=review_id).first()

    if like:
        db.session.delete(like)
    else:
        new_like = Like(user_id=current_user.id, review_id=review_id)
        db.session.add(new_like)
        if dislike:
            db.session.delete(dislike)

    db.session.commit()
    return jsonify({'success': True, 'likes_count': review.likes.count(), 'dislikes_count': review.dislikes.count()})


@main.route('/review/<int:review_id>/dislike', methods=['POST'])
@login_required
def dislike_review(review_id):
    """
    Дизлайк комментария.

    Обрабатывает POST-запросы на добавление и удаление дизлайков к комментариям.
    """
    review = Review.query.get_or_404(review_id)
    dislike = Dislike.query.filter_by(user_id=current_user.id, review_id=review_id).first()
    like = Like.query.filter_by(user_id=current_user.id, review_id=review_id).first()

    if dislike:
        db.session.delete(dislike)
    else:
        new_dislike = Dislike(user_id=current_user.id, review_id=review_id)
        db.session.add(new_dislike)
        if like:
            db.session.delete(like)

    db.session.commit()
    return jsonify({'success': True, 'likes_count': review.likes.count(), 'dislikes_count': review.dislikes.count()})


@main.route('/review/<int:review_id>/delete', methods=['POST'])
@login_required
def delete_review(review_id):
    """
    Удаление комментария.

    Обрабатывает POST-запросы на удаление комментариев и связанных с ними лайков и дизлайков из базы данных.
    """
    review = Review.query.get_or_404(review_id)
    likes = Like.query.filter_by(review_id=review_id).all()
    dislikes = Dislike.query.filter_by(review_id=review_id).all()

    if current_user.id != review.user_id and not current_user.can(Permission.MODERATE):
        return jsonify({'success': False, 'message': 'У вас нет прав на удаление этого отзыва.'})

    for like in likes:
        db.session.delete(like)
    for dislike in dislikes:
        db.session.delete(dislike)

    db.session.delete(review)
    db.session.commit()
    return jsonify({'success': True})


@main.route('/toggle_save', methods=['POST'])
@login_required
def toggle_save():
    """
    Сохранение и удаление товара из избранного.

    Обрабатывает POST-запросы на добавление и удаление товаров из списка сохраненных у текущего пользователя.
    """
    data = request.get_json()
    product_id = data.get('product_id')
    action = data.get('action')

    product = Product.query.get_or_404(product_id)
    saved_product = SavedProduct.query.filter_by(user_id=current_user.id, product_id=product_id).first()

    if action == 'add':
        if saved_product:
            return jsonify(success=False, message="Товар уже в сохраненных")
        else:
            saved_product = SavedProduct(user_id=current_user.id, product_id=product_id)
            db.session.add(saved_product)
            message = "Товар добавлен в сохраненные"
    elif action == 'remove':
        if saved_product:
            db.session.delete(saved_product)
            message = "Товар удален из сохраненных"
        else:
            return jsonify(success=False, message="Товар не найден в сохраненных")
    else:
        return jsonify(success=False, message="Некорректное действие")

    db.session.commit()
    return jsonify(success=True, message=message)
