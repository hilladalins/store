from bottle import route, run, template, static_file, get, post, delete, request
from sys import argv
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


@route('/category', method='POST')
def add_cat():
    result = {}
    result["STATUS"] = 'ERROR'
    try:
        category = request.forms.get('name')
        if not category:
            result["MSG"] = 'Name parameter is missing'
            result["CODE"] = 400
        with connection.cursor() as cursor:
            sql_query = "SELECT * FROM categories WHERE name='{}'".format(category)
            cursor.execute(sql_query)
            response = cursor.fetchone()
            if response:
                result["MSG"] = 'Category already exists'
                result["CODE"] = 200
            else:
                sql_query = "INSERT INTO categories (name) VALUES ('{}')".format(category)
                cursor.execute(sql_query)
                result["STATUS"] = 'SUCCESS'
                result["CODE"] = 201
                result["CAT_ID"] = cursor.lastrowid
    except:
        result["MSG"] = 'Internal error'
        result["CODE"] = 500
    return json.dumps(result)


@delete('/category/<id>')
def delete_cat(id):
    result = {}
    result['STATUS'] = 'ERROR'
    try:
        with connection.cursor() as cursor:
            sql_query = "SELECT * FROM categories WHERE cat_id='{}'".format(id)
            cursor.execute(sql_query)
            response = cursor.fetchone()
            if not response:
                result["MSG"] = 'Category not found'
                result["CODE"] = 404
            sql_query = "DELETE FROM categories WHERE cat_id='{}'".format(id)
            cursor.execute(sql_query)
            result["CODE"] = 201
            result["STATUS"] = 'SUCCESS'
    except:
        result["MSG"] = 'Internal error'
        result["CODE"] = 500
    return json.dumps(result)


@get('/categories')
def categories():
    result = {}
    try:
        with connection.cursor() as cursor:
            sql_query = "SELECT cat_id as id, name FROM categories"
            cursor.execute(sql_query)
            result['CATEGORIES'] = cursor.fetchall()
        result['CODE'] = 200
        result['STATUS'] = 'SUCCESS'
    except:
        result['CODE'] = 500
        result['STATUS'] = 'ERROR'
        result['MSG'] = 'Internal error'
    return json.dumps(result)


@post('/product')
def product():
    result = {}
    try:
        title = request.forms["title"]
        desc = request.forms["desc"]
        price = request.forms["price"]
        img_url = request.forms["img_url"]
        category = request.forms["category"]
        product_id = request.forms["id"]
        favorite = 1 if 'favorite' in request.forms else 0
        if not title or not desc or not price or not img_url or not category:
            result["STATUS"] = "ERROR"
            result["MSG"] = 'missing parameters'
            result["CODE"] = 400
        else:
            with connection.cursor() as cursor:
                sql_query = "SELECT * FROM categories WHERE cat_id={}".format(category)
                cursor.execute(sql_query)
                if not cursor.fetchone():
                    result["STATUS"] = "ERROR"
                    result["MSG"] = 'Category not found'
                    result["CODE"] = 404
        if product_id:
            with connection.cursor() as cursor:
                sql_query = "UPDATE products SET title='{}', desc='{}', price={}," \
                            " img_url='{}', category={}, favorite='{}' WHERE product_id={};"\
                            .format(title, desc, price, img_url, category, favorite, product_id)
                cursor.execute(sql_query)
                result["STATUS"] = "SUCCESS"
                result["PRODUCT_ID"] = product_id
                result["CODE"] = 201
        else:
            with connection.cursor() as cursor:
                sql_query = "INSERT INTO products (title, description, price, img_url, category, favorite) " \
                            "VALUES ('{}', '{}', {}, '{}', {}, '{}')".format(title, desc, price, img_url, category, favorite)
                cursor.execute(sql_query)
                result["STATUS"] = "SUCCESS"
                result["PRODUCT_ID"] = cursor.lastrowid
                result["CODE"] = 201
    except:
        result["STATUS"] = "ERROR"
        result["CODE"] = 500
        result["MSG"] = 'Internal error'
    return json.dumps(result)





run(host='localhost', port=8080)
