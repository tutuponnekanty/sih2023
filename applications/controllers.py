from flask import render_template, request, redirect, session
from flask import current_app as app
from applications.models import User, Product, Purchase, Category
from applications.database import db
from passlib.hash import pbkdf2_sha256 as passhash
from sqlalchemy import func
from collections import Counter
import datetime
import json

#Home
@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "GET":
        query = request.args.get("q")

        if query:
            products = Product.query.filter(Product.name.ilike(f"%{query}%")).all()
        else:
            products = Product.query.all()

        if "user" in session:
            username = session["user"]
            user = User.query.filter_by(username=username).first()
            if user:
                return render_template("home.html", user=username, signed=True, products=products, retailer=user.is_retailer)
            else:
                return render_template("home.html", user=username, signed=True, products=products, retailer=False)
        else:
            return render_template("home.html", user="", signed=False, products=products, retailer=False)
    else:
        product_id, count = request.form["product"], request.form["count"]
        product = Product.query.filter_by(id=product_id).first()

        if product:
            cart = json.loads(session.get("cart", "{}"))
            if product_id in cart:
                current = int(count) + int(cart[product_id])
                if current <= int(product.stock):
                    cart[product_id] = str(int(cart[product_id]) + int(count))
            else:
                current = int(count)
                if current > 0 and current <= int(product.stock):
                    cart[product_id] = count

            session["cart"] = json.dumps(cart)
            print(session["cart"])

        return redirect("/")

# Register
@app.route("/register", methods=["GET", "POST"])
def register():
    if "user" in session:
        return redirect("/")

    if request.method == "GET":
        return render_template("register.html")

    elif request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        name = request.form["name"]
        email = request.form["email"]
        mobile_number = request.form["mobile_number"]
        is_retailer = "retailer" in request.form
        
        existing_user = User.query.filter((User.username == username) | (User.email == email) | (User.mobile_number == mobile_number)).first()

        if existing_user:
            return render_template("error_register.html", message='''OOPS! This username, email, or phone number already exists.''')


        if is_retailer:
            address = request.form["address"]
            aadhar_number = request.form.get("aadhar_number")
            pan_number = request.form.get("pan_number")
            license_id = request.form.get("license_id")
            license_type = request.form.get("license_type")
            company_name = request.form.get("company_name")

            user = User(
                username=username,
                password=password,
                name=name,
                address=address,
                email=email,
                mobile_number=mobile_number,
                aadhar_number=aadhar_number,
                pan_number=pan_number,
                license_id=license_id,
                license_type=license_type,
                company_name=company_name,
                is_retailer=True
            )
        else:
            user = User(
                username=username,
                password=password,
                name=name,
                email=email,
                mobile_number=mobile_number,
                is_retailer=False
            )

        db.session.add(user)
        db.session.commit()

        session["user"] = username
        return redirect("/")

    return render_template("register.html")





# Login
@app.route("/login", methods=["GET", "POST"])
def login():
    if "user" in session:
        return redirect("/")
    if request.method == "GET":
        return render_template("login.html")
    elif request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = User.query.filter_by(username=username).first()
        if not user:
            return render_template("error_login.html", message="User not found.")
        elif user and user.password != password:
            return render_template("error_login.html", message="Incorrect password.")
        
        session["user"] = username
        return redirect("/")
    
# Logout
@app.route("/logout")
def logout():
    if "user" in session:
        session.pop("user")
    return redirect("/")

#Retailer Dashboard

@app.route('/dashboard')
def retailer_dashboard():
    if "user" in session:
        username = session["user"]
        user = User.query.filter_by(username=username).first()
        if user and user.is_retailer:
            products = Product.query.filter_by(owner_id=user.id).all()
            return render_template("dashboard.html", products=products)
    return redirect("/")



#Add Category
@app.route("/add_category", methods=["GET", "POST"])
def add_category():
    if "user" in session:
        user = User.query.filter_by(username=session["user"]).first()
        if user and user.is_retailer:  # Check if user is a retailer
            if request.method == "POST":
                name = request.form["name"]
                description = request.form["description"]
                category = Category(name=name, description=description)
                db.session.add(category)
                db.session.commit()
                return redirect("/dashboard")
            return render_template("add_category.html")
    return redirect("/")

# Add Product
@app.route("/add_product", methods=["GET", "POST"])
def add_product():
    if "user" in session:
        username = session["user"]
        user = User.query.filter_by(username=username).first()
        if user and user.is_retailer:
            if request.method == "POST":
                name = request.form["name"]
                description = request.form["description"]
                stock = request.form["stock"]
                cost = request.form["cost"]
                category_id = request.form["category"]
                img = request.files["img"]

                product = Product(
                    name=name,
                    description=description,
                    stock=stock,
                    cost=cost,
                    category_id=category_id,
                    owner_id=user.id  # Set the owner_id to the current user's id
                )
                db.session.add(product)
                db.session.commit()

                # Save product image
                img.save(f"./static/products/{product.id}.png")

                return redirect("/dashboard")
                
            categories = Category.query.all()
            return render_template("add_product.html", categories=categories)
    return redirect("/")


# Delete Product
@app.route("/delete_product/<product_id>", methods=["GET", "POST"])
def delete_product(product_id):
    if "user" in session:
        user = User.query.filter_by(username=session["user"]).first()
        if user and user.is_retailer:
            if request.method == "GET":
                product = Product.query.get(product_id)
                return render_template("delete_product.html", product=product)
            elif request.method == "POST":
                if "yes" in request.form:
                    product = Product.query.get(product_id)
                    db.session.delete(product)
                    db.session.commit()
                return redirect("/dashboard") 
    return redirect("/")

#Edit Product
@app.route("/edit_product/<product_id>", methods=["GET", "POST"])
def edit_product(product_id):
    if "user" in session:
        user = User.query.filter_by(username=session["user"]).first()
        if user and user.is_retailer:
            product = Product.query.get(product_id)
            if product:
                if request.method == "POST":
                    product.name = request.form["name"]
                    product.description = request.form["description"]
                    product.stock = request.form["stock"]
                    product.cost = request.form["price"] 
                    product.category_id = request.form["category"]
                    db.session.commit()
                    return redirect("/dashboard")
                categories = Category.query.all()
                return render_template("edit_product.html", product=product, categories=categories)
    return redirect("/dashboard")



# Cart
@app.route("/cart", methods=["GET", "POST"])
def cart():
    if "user" in session:
        username = session["user"]
        user = User.query.filter_by(username=username).first()

        if request.method == "POST":
            if "remove" in request.form:
                product_id = request.form["remove"]
                cart = json.loads(session.get("cart", "{}"))

                if product_id in cart:
                    del cart[product_id]

                session["cart"] = json.dumps(cart)

            if "checkout" in request.form:
                cart = json.loads(session.get("cart", "{}"))
                for product_id, count in cart.items():
                    product = Product.query.get(product_id)
                    purchase = Purchase(product_id=product_id, owner_id=user.id, customer_id=user.id, count=count)
                    product.stock -= int(count)
                    db.session.add(purchase)
                    db.session.commit()

                session["cart"] = json.dumps({})

                return redirect("/")

        products = []
        cart = json.loads(session.get("cart", "{}"))
        for product_id, count in cart.items():
            product = Product.query.get(product_id)
            products.append((product, count))

        total = sum(float(product.cost) * int(count) for product, count in products)

        return render_template("cart.html", user=username, signed=True, products=products, total=total, retailer=user.is_retailer)
    else:
        return redirect("/")


# Summary
@app.route('/summary')
def summary():
    

    top_products = db.session.query(Purchase.product_id, func.sum(Purchase.count).label('total_count')) \
        .group_by(Purchase.product_id) \
        .order_by(func.sum(Purchase.count).desc()) \
        .limit(5) \
        .all()

    top_products_info = []
    for product_id, total_count in top_products:
        product = Product.query.get(product_id)
        top_products_info.append({
            'name': product.name,
            'total_count': total_count
        })


    total_money = db.session.query(func.sum(Product.cost * Purchase.count)).scalar()

    sales_data = db.session.query(Product.name, func.sum(Purchase.count).label('total_count')) \
        .join(Purchase, Product.id == Purchase.product_id) \
        .group_by(Product.name) \
        .all()

    return render_template('summary.html', top_products=top_products_info, total_money=total_money, sales_data=sales_data)


#Order History/Purchases
@app.route('/history')
def history():
    if "user" in session:
        username = session["user"]
        user = User.query.filter_by(username=username).first()
        if user:
            purchases = Purchase.query.filter_by(customer_id=user.id).all()
            purchases_with_products = []

            for purchase in purchases:
                product = Product.query.get(purchase.product_id)
                purchases_with_products.append((purchase, product))

            return render_template("order_history.html", user=user, signed=True, purchases=purchases_with_products)
    return redirect("/")


#AboutMission
@app.route('/about')
def about():
    return render_template('about_us.html')

#Search
@app.route("/search", methods=["GET"])
def search():
    query = request.args.get("q")
    products = Product.query.filter(Product.name.ilike(f"%{query}%")).all()
    
    if "user" in session:
        username = session["user"]
        user = User.query.filter_by(name=username).first()  
        return render_template("search.html", user=username, signed=True, products=products, retailer=user.is_retailer)
    else:
        return render_template("search.html", user="", signed=False, products=products, retailer=False)