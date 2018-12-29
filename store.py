from bottle import route, run, template, static_file, get, post, delete, request
import json
from pymysql import connect, cursors


connection = connect(host='localhost',
                     user='root',
                     password='hilla',
                     db='store',
                     charset='utf8',
                     cursorclass=cursors.DictCursor)


@get("/admin")
def admin_portal():
	return template("pages/admin.html")


@get("/")
def index():
    return template("index.html")


@get('/js/<filename:re:.*\.js>')
def javascripts(filename):
    return static_file(filename, root='js')


@get('/css/<filename:re:.*\.css>')
def stylesheets(filename):
    return static_file(filename, root='css')


@get('/images/<filename:re:.*\.(jpg|png|gif|ico)>')
def images(filename):
    return static_file(filename, root='images')


@post('/storename')
def storename():
    try:
        name = request.forms["name"]
        with connection.cursor() as cursor:
            sql_query = "UPDATE store_values SET store_value='{}' WHERE store_key='name'".format(name)
            cursor.execute(sql_query)
            connection.commit()
            result = create_result("SUCCESS", 201)
    except:
        result = create_result("ERROR", 500, "Internal error")
    return json.dumps(result)


@get('/storename')
def storename():
    result = create_result("SUCCESS", 200)
    try:
        with connection.cursor() as cursor:
            sql_query = "SELECT store_value FROM store_values WHERE store_key='name'"
            cursor.execute(sql_query)
            result["name"] = cursor.fetchone()['store_value']
    except:
        result = create_result("ERROR", 500, "Internal error")
    return json.dumps(result)


@post('/category')
def add_cat():
    try:
        category = request.forms.get('name')
        if not category:
            result = create_result('ERROR', 400, 'Name parameter is missing')
        else:
            with connection.cursor() as cursor:
                sql_query = "SELECT * FROM categories WHERE name='{}'".format(category)
                cursor.execute(sql_query)
                response = cursor.fetchone()
                if response:
                    result = create_result('ERROR', 200, 'Category already exists')
                else:
                    sql_query = "INSERT INTO categories (name) VALUES ('{}')".format(category)
                    cursor.execute(sql_query)
                    connection.commit()
                    result = create_result('SUCCESS', 201)
                    result["CAT_ID"] = cursor.lastrowid
    except:
        result = create_result('ERROR', 500, 'Internal error')
    return json.dumps(result)


@delete('/category/<id>')
def delete_cat(id):
    try:
        with connection.cursor() as cursor:
            sql_query = "SELECT * FROM categories WHERE cat_id={}".format(id)
            cursor.execute(sql_query)
            response = cursor.fetchone()
            if not response:
                result = create_result('ERROR', 404, 'Category not found')
            else:
                sql_query = "DELETE FROM categories WHERE cat_id={}".format(id)
                cursor.execute(sql_query)
                connection.commit()
                result = create_result('SUCCESS', 201)
    except:
        result = create_result('ERROR', 500, 'Category not found')
    return json.dumps(result)


@get('/categories')
def categories():
    result = create_result('SUCCESS', 200)
    try:
        with connection.cursor() as cursor:
            sql_query = "SELECT cat_id as id, name FROM categories"
            cursor.execute(sql_query)
            result['CATEGORIES'] = cursor.fetchall()
    except:
        result = create_result('ERROR', 500, 'Internal error')
    return json.dumps(result)


@post('/product')
def product():
    try:
        title = request.forms["title"]
        desc = request.forms["desc"]
        price = request.forms["price"]
        img_url = request.forms["img_url"]
        product_id = request.forms["id"]
        favorite = 1 if 'favorite' in request.forms else 0
        if not title or not desc or not price or not img_url or 'category' not in request.forms:
            result = create_result('ERROR', 400, 'missing parameters')
            return json.dumps(result)
        category = request.forms["category"]
        with connection.cursor() as cursor:
            sql_query = "SELECT * FROM categories WHERE cat_id={}".format(category)
            cursor.execute(sql_query)
            if not cursor.fetchone():
                result = create_result('ERROR', 404, 'Category not found')
                return json.dumps(result)
        if product_id:
            with connection.cursor() as cursor:
                sql_query = "UPDATE products SET title='{}', description='{}', price={}," \
                            " img_url='{}', category={}, favorite='{}' WHERE product_id={};"\
                            .format(title, desc, price, img_url, category, favorite, product_id)
                cursor.execute(sql_query)
                connection.commit()
                result = create_result('SUCCESS', 201)
                result["PRODUCT_ID"] = product_id
        else:
            with connection.cursor() as cursor:
                sql_query = "INSERT INTO products (title, description, price, img_url, category, favorite) " \
                            "VALUES ('{}', '{}', {}, '{}', {}, '{}')".format(title, desc, price, img_url, category, favorite)
                cursor.execute(sql_query)
                connection.commit()
                result = create_result('SUCCESS', 201)
                result["PRODUCT_ID"] = cursor.lastrowid
    except:
        result = create_result('ERROR', 500, 'Internal error')
    return json.dumps(result)


@get('/product/<id>')
def product(id):
    try:
        with connection.cursor() as cursor:
            sql_query = "SELECT title FROM products WHERE product_id={}".format(id)
            cursor.execute(sql_query)
            if not cursor.fetchone():
                result = create_result('ERROR', 404, 'Product not found')
            else:
                sql_query = "SELECT category, description, price, title, favorite, img_url, product_id as id" \
                            " FROM products WHERE product_id={}".format(id)
                cursor.execute(sql_query)
                result = create_result('SUCCESS', 200)
                result["PRODUCT"] = cursor.fetchone()
    except:
        result = create_result('ERROR', 500, 'internal error')
    return json.dumps(result)


@delete('/product/<id>')
def delete_product(id):
    try:
        with connection.cursor() as cursor:
            sql_query = "SELECT title FROM products WHERE product_id={}".format(id)
            cursor.execute(sql_query)
            if not cursor.fetchone():
                result = create_result('ERROR', 404, 'product not found')
            else:
                sql_query = "DELETE FROM products WHERE product_id={}".format(id)
                cursor.execute(sql_query)
                connection.commit()
                result = create_result('SUCCESS', 201)
                result["PRODUCT"] = cursor.fetchone()
    except:
        result = create_result('ERROR', 500, 'internal error')
    return json.dumps(result)


@get('/products')
def products():
    result = create_result('SUCCESS', 200)
    try:
        with connection.cursor() as cursor:
            sql_query = "SELECT category, description, price, title, favorite, img_url, product_id as id FROM products"
            cursor.execute(sql_query)
            result["PRODUCTS"] = cursor.fetchall()
    except:
        result = create_result('ERROR', 500, 'internal error')
    return json.dumps(result)


@get('/category/<id>/products')
def products(id):
    try:
        with connection.cursor() as cursor:
            sql_query = "SELECT title FROM products WHERE category={}".format(id)
            cursor.execute(sql_query)
            if not cursor.fetchone():
                result = create_result('ERROR', 404)
            else:
                sql_query = "SELECT category, description, price, title, favorite+0-1 as favorite, img_url," \
                            " product_id as id FROM products WHERE category={}" \
                            " ORDER BY FIELD(favorite, '1') DESC, creation_date DESC".format(id)
                cursor.execute(sql_query)
                result = create_result('SUCCESS', 200)
                result["PRODUCTS"] = cursor.fetchall()
    except:
        result = create_result('ERROR', 500, 'internal error')
    return json.dumps(result)


def create_result(*args):
    result = {}
    result["STATUS"] = args[0]
    result["CODE"] = args[1]
    if len(args) == 3:
        result["MSG"] = args[2]
    return result


run(host='localhost', port=8080)
