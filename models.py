from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Product(db.Model):
    __tablename__ = "product"
    product_id = db.Column(db.String, primary_key=True)
    name = db.Column(db.String, nullable=False)

    movements = db.relationship("ProductMovement", back_populates="product")


class Location(db.Model):
    __tablename__ = "location"
    location_id = db.Column(db.String, primary_key=True)
    name = db.Column(db.String, nullable=False)

    movements_from = db.relationship(
        "ProductMovement",
        foreign_keys="ProductMovement.from_location",
        back_populates="from_location_rel"
    )
    movements_to = db.relationship(
        "ProductMovement",
        foreign_keys="ProductMovement.to_location",
        back_populates="to_location_rel"
    )


class ProductMovement(db.Model):
    __tablename__ = "productmovement"
    movement_id = db.Column(db.String, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    from_location = db.Column(db.String, db.ForeignKey("location.location_id"), nullable=True)
    to_location = db.Column(db.String, db.ForeignKey("location.location_id"), nullable=True)
    product_id = db.Column(db.String, db.ForeignKey("product.product_id"), nullable=False)

    qty = db.Column(db.Integer, nullable=False)

    # Relationships
    product = db.relationship("Product", back_populates="movements")
    from_location_rel = db.relationship("Location", foreign_keys=[from_location], back_populates="movements_from")
    to_location_rel = db.relationship("Location", foreign_keys=[to_location], back_populates="movements_to")
