from flask import Flask, request, redirect, render_template, url_for, session, jsonify
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash,check_password_hash
from uploader import process
import os 
import uuid
import json
from os.path import join, dirname, realpath

app = Flask(__name__)

app.secret_key = 'the random stringxxxx'

UPLOAD_FOLDER = join(dirname(realpath(__file__)), 'static/upload-files/')



# MySQL Configuration
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_DB'] = 'product'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

# Initialize MySQL
mysql = MySQL(app)

def allowed_file(filename):
  # Add your allowed file extensions here
  ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'b2b'}

  return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/logout")
def logout():
    if "logged_in" in session:
        session.pop('logged_in')
        session.pop('username')
        return redirect(url_for("login"))
    return redirect(url_for("login"))


@app.route('/login', methods=['GET','POST'])
def login():
    if request.method =='POST':
        # Get form data
        username = request.form['username']
        password = request.form['password']

        # Create cursor
        cur = mysql.connection.cursor()

        # Get user by username
        result = cur.execute("SELECT * FROM users WHERE username = %s", [username])

        if result > 0:
            # Get stored hash
            data = cur.fetchone()
            password_hash = data['password']

            # Compare Passwords
            if password_hash == password:
                # Passed
                session['logged_in'] = True
                session['username'] = username

                return redirect(url_for('dashboard'))
            else:
                # Failed
                error = 'Invalid password'
                return render_template('login.html', error=error)
        else:
            # User not found
            error = 'Username not found'
            return render_template('login.html', error=error)
    else:
        return render_template("login.html")



@app.route('/')
def dashboard():
    if "logged_in" in session:
        
        cur = mysql.connection.cursor()
        cur.execute('SELECT COUNT(id) AS NumberOfProducts FROM products;')
        total_products = cur.fetchone()['NumberOfProducts']
        total_uploaded_files = len(os.listdir(UPLOAD_FOLDER))
        return render_template('index.html',username= session['username'],total_products=total_products,uploaded_files=total_uploaded_files)
    else:
        return redirect(url_for('login'))



@app.route('/upload',methods=['GET','POST'])
def upload():
    if "logged_in" in session:
        if request.method=='POST':
            file = request.files.get("file")
            if file and allowed_file(file.filename):
                # Generate a unique file name
                filename = file.filename
                # Save the file
                file.save(os.path.join(UPLOAD_FOLDER, filename))                
                result = process(filename)                    
                print("han bc: ",result)
                if result == "True":
                    return "True"
                    return redirect(url_for("products"))
                elif result=="Invalid Data":
                    error = "Invalid Data, Please make sure that these fields exist and right name as follow: style_name, style_number, cost, manufacturer, retail_price_override, selling_unit_quantity"
                    return error
                    return render_template("upload.html",error=error)
                else:
                    return result
                    return "some error"
            else:
                error = "Invalid File Type"
                return error
                return render_template("upload.html",error="Invalid File type")
            return x
        else:
            return render_template('upload.html',username= session['username'])
    else:
        return redirect(url_for('login'))

@app.route('/products')
def products():
    if "logged_in" in session:
        
        cur = mysql.connection.cursor()
        cur.execute("SELECT * from products;")
        products = cur.fetchall()
        return render_template('products.html',username= session['username'],products=products)
    else:
        return redirect(url_for('login'))

@app.route("/view-product/<int:id>")
def view_product(id):
    if "logged_in" in session:        
        cur = mysql.connection.cursor()
        cur.execute("SELECT * from products where id=%s;",[id])
        product = cur.fetchone()
        if request.args.get("print"):
            return render_template('view-product.html',username= session['username'],product=product,print=True)
        else:
            return render_template('view-product.html',username= session['username'],product=product)
    else:
        return redirect(url_for('login'))

@app.route("/view-product-by-style-number/<string:style_number>")
def view_product_by_sn(style_number): 
    cur = mysql.connection.cursor()
    cur.execute("SELECT * from products where style_number=%s;",[style_number])
    product = cur.fetchone()
    return render_template('view-product.html',username= session['username'],product=product)
    
@app.route("/view-iframe/<int:id>")
def view_iframe(id):
    if "logged_in" in session:
        
        cur = mysql.connection.cursor()
        cur.execute("SELECT * from products where id=%s;",[id])
        product = cur.fetchone()
        return render_template('view-iframe.html',username= session['username'],product=product)
    else:
        return redirect(url_for('login'))
        
@app.route("/print-products",methods=['GET','POST'])
def print_products():
    if "logged_in" in session:
        if request.method == 'POST':            
            data = request.get_json()
            product_ids = data['rows']
            if len(product_ids) != 5:
                return 'False'
            print(product_ids)
            products = []
            for i in product_ids:            
                cur = mysql.connection.cursor()
                cur.execute("SELECT * from products where id=%s;",[i])
                product = cur.fetchone()
                products.append(product)
            return jsonify({"products":products})
        cur = mysql.connection.cursor()
        cur.execute("SELECT * from products;")
        products = cur.fetchall()
        return render_template('print-products.html',username= session['username'],products=products)
    else:
        return redirect(url_for('login'))

@app.route("/print-products-page")
def print_products_page():
    if "logged_in" in session:
        data = request.args.get('data')
        data = json.loads(data)
        products = []
        for i in data['products']:
            products.append(i)
        return render_template('print-products-page.html',username=session['username'],products=products)


    else:
        return redirect(url_for('login'))

@app.route("/account", methods=['GET','POST'])
def account():
    if "logged_in" in session:      
        cur = mysql.connection.cursor()  
        if request.method == 'POST':
            username = request.form.get("username")
            password = request.form.get("password")
            cur.execute("UPDATE users set username=%s,password=%s where id=1;",[username,password])
            mysql.connection.commit()
            session['username'] = username
            return redirect(url_for('account'))
        cur.execute("SELECT * from users where id=1;")
        user = cur.fetchone()
        return render_template("account.html",username=session['username'],user=user)
    else:
        return redirect(url_for('login'))

@app.route("/multiplier",methods=['GET','POST'])
def multiplier():
    if "logged_in" in session:   
        if request.method=='POST':
            cur = mysql.connection.cursor()  
            start = request.form.get("start")
            end = request.form.get("end")
            multiplier = request.form.get("multiplier")
            value = request.form.get("value")
            if multiplier=="add":
                operator = "+"
            elif multiplier=="subtract":
                operator = "-"
            elif multiplier=="multiply":
                operator = "*"
            elif multiplier=="divide":
                operator = "/"
            cur.execute("update products set retail_customer_price =  (retail_customer_price"+operator+value+") where retail_customer_price BETWEEN "+start+" AND "+end+"  ;")
            mysql.connection.commit()
            return redirect(url_for("products"))
            

        return render_template("multiplier.html",username=session['username'])
    else:
        return redirect(url_for('login'))   


@app.route("/truncate-table",methods=['GET','POST'])
def truncate_table():
    if "logged_in" in session:   
        if request.method=='POST':
            password = request.form.get("password")
            cur = mysql.connection.cursor()
            user = cur.execute("SELECT * FROM users WHERE id=1")
            user = cur.fetchone()
            if password==user['password']:
                cur.execute("TRUNCATE products;")
                mysql.connection.commit()
                return redirect(url_for("products"))
            else:
                return render_template("truncate-table.html",username=session['username'],error="Invalid Password!")


        return render_template("truncate-table.html",username=session['username'])
    else:
        return redirect(url_for('login'))   



if __name__ == '__main__':
    app.run(debug=True)
