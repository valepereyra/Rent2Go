"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
from flask import Flask, request, jsonify, url_for, Blueprint,current_app,json
from api.models import db, Costumer, Product, Favorites, Cart, Order, Order_item, Order_status_code, Category
from api.utils import generate_sitemap, APIException
from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from flask_jwt_extended import JWTManager
from flask_mail import Message
import random
import string
import os

# SDK de Mercado Pago
import mercadopago
# Agrega credenciales
sdk = mercadopago.SDK("APP_USR-2815099995655791-092911-c238fdac299eadc66456257445c5457d-1160950667")


api = Blueprint('api', __name__)
# Handle/serialize errors like a JSON object

@api.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_cod

# any other endpoint will try to serve it like a static file
@api.route('/hello', methods=['POST', 'GET'])
def handle_hello():
    response_body = {
        "message": "Hello! I'm a message that came from the backend, check the network tab on the google inspector and you will see the GET request"
    }
    return jsonify(response_body), 200


# -----------------------------------------------------------endpoints --------------------------------- #
    # generate sitemap with all your endpoints
@api.route('/')
def sitemap():
    if ENV == "development":
        return generate_sitemap(app)
    return send_from_directory(static_file_dir, 'index.html')

# any other endpoint will try to serve it like a static file
@api.route('/<path:path>', methods=['GET'])
def serve_any_other_file(path):
    if not os.path.isfile(os.path.join(static_file_dir, path)):
        path = 'index.html'
    response = send_from_directory(static_file_dir, path)
    response.cache_control.max_age = 0 # avoid cache memory
    return response


# ----------------------------------------------------------- MERCADO PAGO --------------------------------- #
@api.route("/preference", methods=["POST"])
def preference():
    body = json.loads(request.data)
    total = body["total"]  
    # Crea un ítem en la preferencia
    preference_data = {
        "items": [
            {
                "title": "Rent2Go",
                "quantity": 1,
                "unit_price":total,
            }
        ],
        "payer":{
            "email":"test_user_17805074@testuser.com"
        },
        "back_urls": {
            "success": "https://3000-nataliagonzalez-rent2go-rmnr5xxntcm.ws-us88.gitpod.io",
            "failure": "https://3000-nataliagonzalez-rent2go-rmnr5xxntcm.ws-us88.gitpod.io",
            "pending": "https://3000-nataliagonzalez-rent2go-rmnr5xxntcm.ws-us88.gitpod.io"
	},
        "auto_return": "approved"
    }

    preference_response = sdk.preference().create(preference_data)
    preference = preference_response["response"]
    return preference, 200

# ----------------------------------------------------------- Login  --------------------------------- #

#---  Ingresando a la pagina (login) ---
@api.route("/login", methods=["POST"])
def login():
    email = request.json.get("email", None)
    password = request.json.get("password", None)
    costumer = Costumer.query.filter_by(email=email, password=password).first()
    if email != costumer.email or password != costumer.password:
        return jsonify({"msg": "Bad email or password"}), 401
    access_token = create_access_token(identity=email)
    return jsonify(access_token=access_token, costumer_id=costumer.id) 

#---  Valid Token ---
@api.route("/valid-token", methods=["GET"])
@jwt_required() #es como el portero que permite o no la entrada; verifica si tiene el token
def valid_token():
    # Access the identity of the current user with get_jwt_identity
    current_costumer = get_jwt_identity()

    costumer = Costumer.query.filter_by(email=current_costumer).first()

    if costumer is None:
        return jsonify({"status": False}), 404

    response_body = {
        
        "costumer": costumer.serialize(),
        "status": True
    }


    return jsonify(response_body), 200

# ----------------------------------------------------------- Productos--------------------------------- #


#--- OBTENIENDO un producto por id --- 
@api.route('/costumer/<int:costumer_id>/product/detail/<int:id>', methods=['GET'])
def handle_product_detail(costumer_id,id):
    productsDetail = Product.query.filter_by(costumer_id=costumer_id,id=id).all()
    results = list(map(lambda item: item.serialize(),productsDetail))
    return jsonify(results), 200   

#--- agregando post de product ---
@api.route('/product', methods=['POST'])
def add_new_product():
    request_body = request.json
    print(
        request_body["images"][0]
    )
    new_product = Product(name=request_body["name"], description=request_body["description"],image=request_body["images"][0],image2=request_body["images"][1],image3=request_body["images"][2],image4=request_body["images"][3] ,price=request_body["price"],costumer_id=request_body["costumer_id"],category_id=request_body["category_id"])
    db.session.add(new_product)
    db.session.commit()
    return jsonify({"msg":"Producto creado correctamente"}),200

#---  obteniendo info de todos los productos ---
@api.route('/products', methods=['GET'])
def handle_products():
    allproducts = Product.query.all()
    print(allproducts)
    results = list(map(lambda item: item.serialize(),allproducts))
    print(results)
    return jsonify(results), 200

#---  obteniendo info de todos los productos ---
@api.route('/editprofile', methods=['GET'])
def handle_profile():
    profile = Costumer.query.all()
    print(profile)
    results = list(map(lambda item: item.serialize(),profile))
    print(results)
    return jsonify(results), 200

#---  eliminando un producto ---
@api.route("/costumer/<int:costumer_id>/product/<int:id>", methods=["DELETE"])
def del_product(costumer_id, id):
    product = Product.query.filter_by(costumer_id=costumer_id).filter_by(id=id).first()
    if product is not None:
        db.session.delete(product)
        db.session.commit()
        return jsonify("El producto ha sido eliminado"), 200
    else:
        return jsonify("No hemos podido encontrar este producto"), 404
    
#---  eliminando todos los productos---
@api.route("/costumer/<int:costumer_id>/products", methods=["DELETE"])
def del_all_products(costumer_id):
    delAllProducts = Product.query.filter_by(costumer_id=costumer_id).all()
    print(delAllProducts)
    if delAllProducts == []:
        return jsonify("No hemos podido encontrar este producto"), 404
        
    else:   
        for o in delAllProducts:
            db.session.delete(o)
            db.session.commit()
        return jsonify("Todos los productos han sido eliminados"), 200

# ----------------------------------------------------------- RECUPERACION CONTRASEÑA OLVIDADA --------------------------------- #

#---  POST  Recuperar contraseña --
@api.route("/forgotpassword", methods=["POST"])
def forgotpassword():
    recover_email = request.json['email']
    recover_password = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(8))
    # 1) clave aleatoria nueva 
    if not recover_email:
        return jsonify({"msg": "Debe ingresar el correo"}), 401
    #2) busco si el correo existe en mi base de datos
    costumer = Costumer.query.filter_by(email=recover_email).first()
    if recover_email != costumer.email:
        return jsonify({"msg": "El correo ingresado no existe en nuestros registros"}), 400
    #3) si existe guardo la nueva contraseña aleatoria
    costumer.password = recover_password
    db.session.commit()
    #4) luego se la envio al usuario por correo para que pueda ingresar
    msg = Message("Hi", recipients=[recover_email])
    msg.html = f"""<h1>Su nueva contraseña es: {recover_password}</h1>"""
    current_app.mail.send(msg)
    return jsonify({"msg": "Su nueva clave ha sido enviada al correo electrónico ingresado"}), 200


# ----------------------------------------------------------- Favoritos --------------------------------- #

#---  Obteniendo info de todos los favoritos ---
@api.route('/favorites/<int:costumer_id>', methods=['GET'])
def handle_favorites(costumer_id):
    allfavorites = Favorites.query.filter_by(costumer_id=costumer_id).all()
    results = list(map(lambda item:{**item.serialize(),**item.serialize3()},allfavorites))
    return jsonify(results), 200




#---  agregando productos a favoritos ---
@api.route("/costumer/<int:costumer_id>/favorites/<int:id>", methods=["POST"])
def add_favorites(costumer_id, id):
    addfavorites = Favorites.query.filter_by(costumer_id=costumer_id, product_id=id).first()
    if addfavorites is None:
        newFav = Favorites(costumer_id=costumer_id,product_id=id,status=True)
        db.session.add(newFav)
        db.session.commit()
        activeFav = Favorites.query.filter_by(costumer_id=costumer_id, status=True).all()
        results = list(map(lambda item:{**item.serialize(),**item.serialize3()},activeFav))
        return jsonify(results), 200
    else:
        return jsonify("Este producto ya existe"), 400

#---  eliminando un producto de favoritos ---
@api.route("/costumer/<int:costumer_id>/favorites/<int:id>", methods=["DELETE"])
def del_favorites(costumer_id, id):
    favorites = Favorites.query.filter_by(costumer_id=costumer_id, product_id=id).first()
    if favorites is not None:
        db.session.delete(favorites)
        db.session.commit()
        return jsonify("El producto ha sido eliminado"), 200
    else:
        return jsonify("No hemos podido encontrar este producto"), 404

    
#---  eliminando todos los productos de favoritos ---
@api.route("/costumer/<int:costumer_id>/favorites", methods=["DELETE"])
def del_all_favorites(costumer_id):
    delAll = Favorites.query.filter_by(costumer_id=costumer_id).all()
    print(delAll)
    if delAll == []:
        return jsonify("No hemos podido encontrar este producto"), 404
        
    else:   
        for o in delAll:
            db.session.delete(o)
            db.session.commit()
        return jsonify("Todos los productos han sido eliminados"), 200 

# ----------------------------------------------------------- Costumer --------------------------------- #

#---  Creando un nuevo usuario  ---
@api.route('/register', methods=['POST'])
def crear_Usuario():
    request_body = request.json #Guardo la respuesta que trae la solicitud en una variable que se llama "request_body" que es un objeto
    print(request_body)
    get_costumer = Costumer.query.filter_by(email = request_body["email"]).first() #Filtro User para que me diga si este email ya esta registrado
    if get_costumer is None: #si no esta registrado que cree uno
        crear_nuevo_usuario = Costumer(email= request_body["email"] , username = request_body["username"], password= request_body["password"])
        db.session.add(crear_nuevo_usuario)
        db.session.commit()
        return jsonify({"msg":"Nuevo usuario ha sido creado"}), 200
    else:
        return jsonify({"msg":"El email ya esta registrado."}), 400

#---  Obtener info de customer ---
@api.route('/register', methods=['GET'])
def handle_costomer():
    allcostumer = Costumer.query.all()
    print(allcostumer)
    results = list(map(lambda item: item.serialize(),allcostumer))
    print(results)
    return jsonify(results), 200

#---  obtener info category todos ---
@api.route('/category', methods=['GET'])
def handle_category():
    allcategory = Category.query.all()
    print(allcategory)
    results = list(map(lambda item: item.serialize(),allcategory))
    print(results)
    return jsonify(results), 200

#---  Obteniendo el producto dentro de una categoria---
@api.route('/category/<int:category_id>/products/', methods=['GET'])
def get_products_category(category_id):
    
    category_products = Product.query.filter_by(category_id=category_id).all()
    results = list(map(lambda item: item.serialize(),category_products))
    return jsonify(results), 200

#---  obtener info category solo 1 ---
@api.route('/category/<int:category_id>', methods=['GET'])
def handle_category_varios(category_id):
    category_one = Category.query.filter_by(id=category_id).first()
    return jsonify(category_one.serialize()), 200

#---  Obteniendo info de un solo product---
@api.route('/product/<int:product_id>', methods=['GET'])
def get_info_product(product_id): 
    product = Product.query.filter_by(id=product_id).first()
    return jsonify(product.serialize()), 200

#---  Completando el perfil ---
@api.route('/editprofile/<int:id>', methods=['PUT'])
def edit_profile(id):
    customer = Costumer.query.get(id)
    if not customer:
        return jsonify({"msg": "El usuario no existe"}), 404

    request_body = request.json
    customer.name = request_body.get("name", customer.name)
    customer.email = request_body.get("email", customer.email)
    customer.password = request_body.get("password", customer.password)
    customer.username = request_body.get("username", customer.username)
    customer.lastName = request_body.get("lastName", customer.lastName)
    customer.address = request_body.get("address", customer.address)
    customer.role = request_body.get("role", customer.role)
    customer.phone = request_body.get("phone", customer.phone)
    customer.image = request_body.get("image", customer.image)

    db.session.commit()
    return jsonify({"msg":"Datos de perfil actualizados de forma satisfactoria"}), 200


# -----------------------------------------------------------CART--------------------------------- # 

#---  AGREGANDO un producto al carrito ---
@api.route("/costumer/<int:costumer_id>/cart/<int:id>", methods=["POST"])
def add_cart(costumer_id,id):
    request_body = request.json
    addcart = Cart.query.filter_by(costumer_id=costumer_id, product_id=id).first()
    if addcart is None:
        newAddCart= Cart(costumer_id=costumer_id,product_id=id,quantity=request_body["quantity"],status=True)
        db.session.add(newAddCart)
        db.session.commit()
        activeCart = Cart.query.filter_by(costumer_id=costumer_id, status=True).all()
        results = list(map(lambda item:{**item.serialize(),**item.serialize2()},activeCart))
        return jsonify(results), 200
    else:
        return jsonify("Este producto ya existe"), 400

# #---  Traer un producto del carrito ---

@api.route('/cart/<int:costumer_id>', methods=['GET'])
def cart(costumer_id):
    allcart = Cart.query.filter_by(costumer_id=costumer_id).all()
    print(allcart)
    results = list(map(lambda item:{**item.serialize(),**item.serialize2()},allcart))
    print(results)
    return jsonify(results), 200

#---  eliminando un product de cart ---
@api.route("/costumer/<int:costumer_id>/cart/<int:id>", methods=["DELETE"])
def del_cart(costumer_id, id):
    cart = Cart.query.filter_by(costumer_id=costumer_id).filter_by(product_id=id).first()
    if cart is not None:
        db.session.delete(cart)
        db.session.commit()
        return jsonify("El producto ha sido eliminado"), 200
    else:
        return jsonify("No hemos podido encontrar este producto"), 404
    
#---  eliminando todos los productos de cart ---
@api.route("/costumer/<int:costumer_id>/cart", methods=["DELETE"])
def del_all_cart(costumer_id):
    delAllCart = Cart.query.filter_by(costumer_id=costumer_id).all()
    print(delAllCart)
    if delAllCart == []:
        return jsonify("No hemos podido encontrar este producto"), 404
        
    else:   
        for o in delAllCart:
            db.session.delete(o)
            db.session.commit()
        return jsonify("Todos los productos han sido eliminados"), 200

## ------> Actualizando Productos

@api.route('/product/<int:id>', methods=['PUT'])
def update_product(id):

    product = Product.query.get(id)

    if product is None:
        return jsonify({'error': 'Producto no encontrado.'}), 404

    request_body = request.json
    if 'name' in request_body:
        product.name = request_body['name']
    if 'description' in request_body:
        product.description = request_body['description']
    if 'image' in request_body:
        product.image = request_body['image']
    if 'price' in request_body:
        product.price = request_body['price']
    if 'costumer_id' in request_body:
        product.costumer_id = request_body['costumer_id']
    if 'category_id' in request_body:
        product.category_id = request_body['category_id']

    db.session.commit()

    return jsonify({'msg': 'Producto actualizado correctamente.'}), 200

#---  Mostrar order ---#

@api.route('/order/<int:costumer_id>', methods=['GET'])
def orders(costumer_id):
    allorders = Order.query.filter_by(costumer_id=costumer_id).all()
    print(allorders)
    results = list(map(lambda item:{**item.serialize(),**item.serialize6()},allorders))
    print(results)
    return jsonify(results), 200

#---  Mostrar order_item ---#

@api.route('/order_item', methods=['GET'])
def orders_item():
    allorders_items = Order_item.query.all()
    print(allorders_items)
    results = list(map(lambda item: item.serialize(),allorders_items))
    print(results)
    return jsonify(results), 200

#---  Mostrar order_status_code ---#

@api.route('/order_status_code', methods=['GET'])
def orders_status():
    allorders_status = Order_status_code.query.all()
    print(allorders_status)
    results = list(map(lambda item: item.serialize(),allorders_status))
    print(results)
    return jsonify(results), 200

#---  Mostrar order_item segun el producto---#

@api.route('/order_item/<int:product_id>', methods=['GET'])
def orders_item_product(product_id):
    allorders_items_products = Order_item.query.filter_by(product_id=product_id).all()
    print(allorders_items_products)
    results = list(map(lambda item:{**item.serialize(),**item.serialize4(),**item.serialize5(),**item.serialize7()},allorders_items_products))
    print(results)
    return jsonify(results), 200
