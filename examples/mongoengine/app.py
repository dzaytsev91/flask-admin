import datetime
from math import ceil

from flask import Flask
from mongoengine import StringField, ListField, EmbeddedDocumentListField

from flask_admin import expose

import flask_admin as admin
from flask_mongoengine import MongoEngine
from flask_admin.form import rules
from flask_admin.contrib.mongoengine import ModelView

# Create application
app = Flask(__name__)

# Create dummy secrey key so we can use sessions
app.config['SECRET_KEY'] = '123456790'
app.config['MONGODB_SETTINGS'] = {'DB': 'testing'}

# Create models
db = MongoEngine()
db.init_app(app)


class CheckData(db.EmbeddedDocument):
    fiscal_drive_number = db.StringField(max_length=255, required=True)
    fiscal_document_number = db.StringField(max_length=255, required=True)
    fiscal_sign = db.StringField(max_length=255, required=True)
    date = db.DateTimeField()
    sum = db.IntField()
    inn = db.StringField(max_length=255, required=True)
    payment_type = db.StringField(max_length=128)
    qr_string = db.StringField(max_length=255, required=True)


class CheckProperties(db.EmbeddedDocument):
    ip = db.StringField(max_length=45, required=True)
    scan_time = db.DateTimeField()


class CheckItems(db.EmbeddedDocument):
    uuid = db.StringField(max_length=36, required=True)
    description = db.StringField(max_length=1024, required=True)
    price = db.IntField()
    quantity = db.IntField()
    positions_count = db.IntField()
    alias_id = db.ObjectIdField()
    brand_id = db.IntField()
    segment_id = db.IntField()


class Check(db.EmbeddedDocument):
    uuid = db.StringField(max_length=36, required=True)
    status = db.StringField(max_length=55, required=True)
    device_id = db.StringField(max_length=36, required=True)
    geo_id = db.IntField()
    affiliate_id = db.ObjectIdField()
    data = db.EmbeddedDocumentField(CheckData)
    items = db.ListField(db.EmbeddedDocumentField(CheckItems))
    created_at = db.DateTimeField()
    updated_at = db.DateTimeField()


class TransactionProperties(db.EmbeddedDocument):
    ip = db.StringField(max_length=45)


class Transactions(db.EmbeddedDocument):
    uuid = db.StringField(max_length=36, required=True)
    amount = db.IntField()
    direction = db.StringField(max_length=36, required=True)
    status = db.StringField(max_length=64, required=True)
    payment_method_id = db.ObjectIdField()
    message = db.StringField(max_length=255, required=True)
    kassa_transaction_id = db.StringField(max_length=24, required=True)
    # in_transactions_ids = db.ListField(db.ObjectIdField())
    properties = db.EmbeddedDocumentField(TransactionProperties)


class UserState(db.EmbeddedDocument):
    status = db.StringField(max_length=255)
    balance = db.IntField()


class PaymentMethod(db.EmbeddedDocument):
    uuid = db.StringField(max_length=36)
    type = db.StringField(max_length=255)
    value = db.StringField(max_length=255)
    description = db.StringField(max_length=255)
    deleted_at = db.DateTimeField()


class User(db.Document):
    uid = db.StringField(max_length=36)
    checks = db.ListField(db.EmbeddedDocumentField(Check))
    transactions = db.ListField(db.EmbeddedDocumentField(Transactions))
    state = db.EmbeddedDocumentField(UserState)
    payment_methods = db.ListField(db.EmbeddedDocumentField(PaymentMethod))


class EmbeddedRoomImages(db.EmbeddedDocument):
    position = db.IntField()
    image = db.ImageField(size=(1920, 950), thumbnail_size=(640, 316))
    is_main = db.BooleanField()
    is_enabled = db.BooleanField()
    image_big_link = db.StringField()
    image_thumb_link = db.StringField()


class Room(db.Document):
    images = db.ListField(db.EmbeddedDocumentField(EmbeddedRoomImages))


class UserView(ModelView):
    pass
#     form_subdocuments = {
#         'payment_methods': {
#             'form_subdocuments': {
#                 None: {
#                     # Add <hr> at the end of the form
#                     # 'form_rules': ('name', 'tag', 'value', rules.HTML('<hr>')),
#                     # 'form_widget_args': {
#                     #     'name': {
#                     #         'style': 'color: red'
#                     #     }
#                     # }
#                 }
#             }
#         }
#     }


class RoomView(ModelView):
    pass


class ChecksView(ModelView):

    def get_query(self):
        """
        Returns the QuerySet for this view.  By default, it returns all the
        objects for the current model.
        """
        checks = []
        users = self.model.objects.only('checks')
        for user in users:
            for check in user.checks:
                checks.append(check)
        import ipdb; ipdb.set_trace();
        return checks


# Flask views
@app.route('/')
def index():
    return '<a href="/admin/">Click me to get to Admin!</a>'


if __name__ == '__main__':
    # Create admin
    admin = admin.Admin(app, 'Example: MongoEngine')

    # Add views
    admin.add_view(UserView(User))
    admin.add_view(RoomView(Room))
    admin.add_view(ChecksView(User, endpoint='testing'))
    # admin.add_view(ModelView(Tag))
    # admin.add_view(PostView(Post))
    # admin.add_view(ModelView(File))
    # admin.add_view(ModelView(Image))

    # Start app
    app.run(debug=True)
