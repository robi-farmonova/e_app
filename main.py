from flask import Flask, render_template, request, url_for, redirect, session, flash, get_flashed_messages
import db
app = Flask(__name__)
app.secret_key = "dont_ask_please"

products = db.products
categories_id = db.categories_id
users = db.users



@app.route('/')
def home():
    data = {}
    for i in categories_id.values():
        data[i] = len(products[i])
    return render_template("home.html", data = data.items())



@app.route('/view')
@app.route('/view/<category>')
@app.route('/view/<category>/<product_id>')
def view(category=None, product_id=None):
    if category and product_id:
        img_path = f'images/{category}/{product_id}.jpg'
        return render_template("view.html", product = products[category][product_id], img_path=img_path)
    elif category:
        p = products[category]
        a = []
        for i in p.values():
            i["img_path"] = f'images/{i["category"]}/{i["id"]}.jpg'
            a.append(i)
        return render_template("products.html", products=a)
    else:
        a = []
        for i in products.values():
            for j in i.values():
                j["img_path"] = f'images/{j["category"]}/{j["id"]}.jpg'
                a.append(j)
        return render_template("products.html", products=a)



@app.route("/signup", methods=["GET", "POST"])
def signup():
    problem = False
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]
        for x in users:
            user = users[x]
            if user["username"] == username or user["email"] == email:
                flash("Username or Email already exists!", "error")
                problem = True
        if not problem:
            n = len(users)+1
            users[n] = {"username": username, "pass": password, "email": email}
            return redirect(url_for("login"))

    return render_template("signup.html")



@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        for user_id, user in users.items():
            if user["username"] == username and user["pass"] == password:
                session["username"] = username
                return redirect(url_for("home"))
        flash("Invalid email or password!", "error")

    return render_template("login.html")



@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))


@app.route("/cart")
def cart():
    cart_items = session.get("cart", [])  # Agar cart mavjud bo'masa bo'sh royxat qaytaradi
    total = 0
    for i in cart_items:
        total += float(i['price'])*int(i['quantity'])
        if total == round(total):
            total = int(total)
        img_path = f'images/{i["category"]}/{i["product_id"]}.jpg'
        i['img_path'] = img_path
    return render_template("cart.html", cart=cart_items, total=total)


@app.route('/add-to-cart', methods=['POST'])
def add_to_cart():
    product_id = request.form['product_id']
    category = request.form['category']
    if session.get('username'):     
        quantity = int(request.form['quantity'])
        name = products[category][product_id]['name']
        price = products[category][product_id]['price']
        cart = session.get('cart', [])
        x = []
        old_quantity = 0
        if not cart: cart = []
        for p in cart:
            if p['category'] == category and p['product_id'] == product_id:
                old_quantity = int(p['quantity'])
            else:
                x.append(p)
        x.append({'category':category, 'product_id':product_id, 'name':name, 'price':price, 'quantity':quantity+old_quantity})
        session['cart'] = x
        print(x)
        if quantity>1: s = "s"
        else: s = ""
        flash(f"{quantity} item{s} added!", "success")
    flash("Sign Up or Login first!", "error")
    img_path = f'images/{category}/{product_id}.jpg'
    print(get_flashed_messages())
    return render_template("view.html", product = products[category][product_id], img_path=img_path)


@app.route('/remove-from-cart/<category>/<product_id>')
def remove_from_cart(category, product_id):
    cart = session.get('cart')
    a = []
    for i in cart:
        if i['category'] == category and i['product_id'] == product_id:
            continue
        a.append(i)
    session['cart'] = a
    return redirect(url_for('cart'))

@app.route('/plus-item/<category>/<product_id>')
def plus_item(category, product_id):
    cart = session.get('cart')
    a = []
    for i in cart:
        if i['category'] == category and i['product_id'] == product_id:
            i['quantity'] = int(i['quantity']) + 1
        a.append(i)
    session['cart'] = a
    return redirect(url_for('cart'))

@app.route('/minus-item/<category>/<product_id>')
def minus_item(category, product_id):
    cart = session.get('cart')
    a = []
    for i in cart:
        if i['category'] == category and i['product_id'] == product_id:
            i['quantity'] = int(i['quantity']) - 1
            if int(i['quantity']) == 0:
                continue
        a.append(i)
    session['cart'] = a
    return redirect(url_for('cart'))

if __name__ == '__main__':
    app.run(debug=True) 