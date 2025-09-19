from flask import Flask, render_template, request, redirect, url_for
from models import db, Product, Location, ProductMovement
from collections import defaultdict
import uuid

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///inventory.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

with app.app_context():
    db.create_all()

# ---------------- PRODUCTS ----------------
@app.route("/")
def products():
    return render_template("products.html", products=Product.query.all())

@app.route("/product/add", methods=["GET", "POST"])
def add_product():
    if request.method == "POST":
        product = Product(product_id=str(uuid.uuid4()), name=request.form["name"])
        db.session.add(product)
        db.session.commit()
        return redirect(url_for("products"))
    return render_template("product_form.html", action="Add", product=None)

@app.route("/product/edit/<product_id>", methods=["GET", "POST"])
def edit_product(product_id):
    product = Product.query.get_or_404(product_id)
    if request.method == "POST":
        product.name = request.form["name"]
        db.session.commit()
        return redirect(url_for("products"))
    return render_template("product_form.html", action="Edit", product=product)

@app.route("/product/delete/<product_id>", methods=["POST"])
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    return redirect(url_for("products"))

# ---------------- LOCATIONS ----------------
@app.route("/locations")
def locations():
    return render_template("locations.html", locations=Location.query.all())

@app.route("/location/add", methods=["GET", "POST"])
def add_location():
    if request.method == "POST":
        location = Location(location_id=str(uuid.uuid4()), name=request.form["name"])
        db.session.add(location)
        db.session.commit()
        return redirect(url_for("locations"))
    return render_template("location_form.html", action="Add", location=None)

@app.route("/location/edit/<location_id>", methods=["GET", "POST"])
def edit_location(location_id):
    location = Location.query.get_or_404(location_id)
    if request.method == "POST":
        location.name = request.form["name"]
        db.session.commit()
        return redirect(url_for("locations"))
    return render_template("location_form.html", action="Edit", location=location)

@app.route("/location/delete/<location_id>", methods=["POST"])
def delete_location(location_id):
    location = Location.query.get_or_404(location_id)
    db.session.delete(location)
    db.session.commit()
    return redirect(url_for("locations"))

# ---------------- MOVEMENTS ----------------
@app.route("/movements")
def movements():
    return render_template("movements.html", movements=ProductMovement.query.all())

@app.route("/movement/add", methods=["GET", "POST"])
def add_movement():
    if request.method == "POST":
        move = ProductMovement(
            movement_id=str(uuid.uuid4()),
            product_id=request.form["product_id"],
            from_location=request.form.get("from_location") or None,
            to_location=request.form.get("to_location") or None,
            qty=int(request.form["qty"]),
        )
        db.session.add(move)
        db.session.commit()
        return redirect(url_for("movements"))
    return render_template(
        "movement_form.html",
        products=Product.query.all(),
        locations=Location.query.all(),
        action="Add",
        movement=None
    )

@app.route("/movement/edit/<movement_id>", methods=["GET", "POST"])
def edit_movement(movement_id):
    movement = ProductMovement.query.get_or_404(movement_id)
    if request.method == "POST":
        movement.product_id = request.form["product_id"]
        movement.from_location = request.form.get("from_location") or None
        movement.to_location = request.form.get("to_location") or None
        movement.qty = int(request.form["qty"])
        db.session.commit()
        return redirect(url_for("movements"))
    return render_template(
        "movement_form.html",
        products=Product.query.all(),
        locations=Location.query.all(),
        action="Edit",
        movement=movement
    )

@app.route("/movement/delete/<movement_id>", methods=["POST"])
def delete_movement(movement_id):
    movement = ProductMovement.query.get_or_404(movement_id)
    db.session.delete(movement)
    db.session.commit()
    return redirect(url_for("movements"))

# ---------------- REPORT ----------------
@app.route("/report", methods=["GET", "POST"])
def report():
    search_product = request.form.get("search_product", "")
    balances = defaultdict(lambda: defaultdict(int))
    for move in ProductMovement.query.all():
        if move.from_location:
            balances[move.product_id][move.from_location] -= move.qty
        if move.to_location:
            balances[move.product_id][move.to_location] += move.qty

    rows = []
    for pid, locs in balances.items():
        product = Product.query.get(pid)
        product_name = product.name if product else f"Unknown ({pid})"
        if search_product and search_product.lower() not in product_name.lower():
            continue
        for lid, qty in locs.items():
            location = Location.query.get(lid)
            location_name = location.name if location else f"Unknown ({lid})"
            rows.append({
                "product": product_name,
                "location": location_name,
                "qty": qty
            })
    return render_template("report.html", rows=rows, search_product=search_product)

if __name__ == "__main__":
    app.run(debug=True)
