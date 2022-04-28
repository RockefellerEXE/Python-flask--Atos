
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from sqlite3 import OperationalError


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///database.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
ma = Marshmallow(app)


class ShopingList(db.Model):
    __tablename__ = "shopingList"
    id = db.Column(db.Integer, primary_key=True)
    list_name = db.Column(db.String(200), nullable=False)
    items = db.relationship(
        'Item', cascade='all,delete', backref='shopingList')


class Item(db.Model):
    __tablename__ = "item"
    id = db.Column(db.Integer, primary_key=True)
    item_name = db.Column(db.String(200), nullable=False)
    purchased = db.Column(db.Boolean, default=False, nullable=False)
    shoping_list_id = db.Column(db.Integer, db.ForeignKey('shopingList.id'))


class ItemSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Item
        include_fk = True


class ListSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = ShopingList
    items = ma.Nested(ItemSchema, many=True)


list_schema = ListSchema()
lists_schema = ListSchema(many=True)
item_schema = ItemSchema()
items_schema = ItemSchema(many=True)


# TODO
# sprwdzić poprawność

@app.route('/')
def index():
    return "List menager"

# adding a new list


@app.route('/addList/<string:name>', methods=['POST'])
def add_list(name):
    new_list = ShopingList(list_name=name)
    try:
        db.session.add(new_list)
        db.session.commit()
        return list_schema.dump(new_list)
    except:
        return "Failed to create list"

# adding item to existing list


@app.route('/addItem/<int:list_id>/<string:item_name>', methods=['POST'])
def add_item(list_id, item_name):
    new_item = Item(item_name=item_name, shoping_list_id=list_id)
    my_list = ShopingList.query.get(list_id)
    if my_list is not None:
        try:
            db.session.add(new_item)
            db.session.commit()
            return item_schema.jsonify(new_item)
        except:
            return "Failed to add item"
    else:
        return "List with specified id does not exist"

# list name change


@app.route('/editList/<int:list_id>/<string:new_name>', methods=['PUT'])
def edit_list(list_id, new_name):
    my_list = ShopingList.query.get(list_id)
    if my_list is not None:
        try:
            my_list.list_name = new_name
            db.session.commit()
            return list_schema.dump(my_list)
        except:
            return "Failed to edit list"
    else:
        return "List with specified id does not exist"

# change item status to purchased


@app.route('/setPurchased/<int:id>', methods=['PUT'])
def set_purchased(id):
    item_to_set = Item.query.get(id)
    if item_to_set is not None:
        try:
            item_to_set.purchased = True
            db.session.commit()
            return item_schema.dump(item_to_set)
        except:
            return "Failed to change product status"
    else:
        return "Item with specified id does not exist"

# Remove an item from the list (item id)


@app.route('/deleteItem/<int:item_id>', methods=['DELETE'])
def delete_item(item_id):
    item_to_delete = Item.query.get(item_id)
    if item_to_delete is not None:
        try:
            db.session.delete(item_to_delete)
            db.session.commit()
            return "Item successfully deleted"
        except:
            return "Failed to delete product"
    else:
        return "Item with specified id does not exist"

# Remove the list with the items


@app.route('/deleteList/<int:list_id>', methods=['DELETE'])
def delete_list(list_id):
    list_to_delete = ShopingList.query.get(list_id)
    if list_to_delete is not None:
        try:
            db.session.delete(list_to_delete)
            db.session.commit()
            return "The list has been deleted successfully"
        except:
            return "Failed to delete list"
    else:
        return "List with specified id does not exist"

# get a list with specified id


@app.route('/getList/<int:list_id>', methods=['GET'])
def get_list(list_id):
    mylist = ShopingList.query.get(list_id)
    if mylist is not None:
        return list_schema.dump(mylist)
    else:
        return "List with specified id does not exist"

# get all lists


@app.route('/getLists', methods=['GET'])
def get_lists():
    my_lists = ShopingList.query.all()
    if my_lists != []:
        return lists_schema.jsonify(my_lists)
    else:
        return "No lists in database"

# get item with specified id


@app.route('/getItem/<int:item_id>', methods=['GET'])
def get_item(item_id):
    my_item = Item.query.get(item_id)
    if my_item is not None:
        return item_schema.dump(my_item)
    else:
        return "Item with specified id does not exist."

# get all items


@app.route('/getItems', methods=['GET'])
def get_items():
    my_items = Item.query.all()
    if my_items != []:
        return items_schema.jsonify(my_items)
    else:
        return "No items"


if __name__ == '__main__':
    db.create_all()

    app.run(debug=True)
