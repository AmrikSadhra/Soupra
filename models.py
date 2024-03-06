from mongoengine import *
from datetime import datetime


class Supra(Document):
    registration = StringField(required=True)
    year = IntField(required=True)
    price = IntField(required=True)
    mileage = IntField(required=True)
    distance = IntField(required=True)
    sold = BooleanField()
    date_added = DateTimeField(required=True)
    date_sold = DateTimeField()

    def __init__(self, registration, year, price, mileage, distance, *args, **values):
        super().__init__(*args, **values)
        self.registration = registration
        self.year = year
        self.price = price
        self.mileage = mileage
        self.distance = distance
        self.date_added = datetime.now()
        self.sold = False

    def __str__(self):
        return "{} | {} | {} GBP | {} miles | {} miles away | {} {}".format(self.registration, self.year, self.price,
                                                                         self.mileage,
                                                                         self.distance,
                                                                         "Sold, on market for:" if self.sold else "Available",
                                                                         self.date_sold - self.date_added if self.sold else "")
