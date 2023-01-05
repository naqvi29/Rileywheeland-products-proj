
from os.path import join, dirname, realpath
import os
import csv
from flask import Flask
from flask_mysqldb import MySQL
import qrcode
import xlrd
import pandas as pd

app = Flask(__name__)
# MySQL Configuration
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_DB'] = 'product'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

# Initialize MySQL
mysql = MySQL(app)

UPLOAD_FOLDER = join(dirname(realpath(__file__)), 'static/upload-files/')
QR_FOLDER = join(dirname(realpath(__file__)), 'static/QR-codes/')
def process(filename):    
    if filename.endswith(".csv"):
        with open(os.path.join(UPLOAD_FOLDER,filename), 'r') as f:
            # Read the CSV file
            reader = csv.reader(f)

            # Get the headers from the first line
            headers = next(reader)

            # Initialize an empty list to store the product data
            products = []
            
            cur = mysql.connection.cursor()

            # Iterate through the rows
            for row in reader:
                # Create a dictionary for the product data
                product = {}

                # Map the headers to the values
                for i, header in enumerate(headers):
                    product[header] = row[i]

                    # Add the product data to the list
                # products.append(product)

                if "cost" in product and "style_number" in product and "style_name" in product and "retail_price_override" in product and "manufacturer" in product and "selling_unit_quantity" in product:
                    qr_code = qrcode.make('/view-product-by-style-number/'+product['style_number'])
                    # Save image to a file
                    qr_code.save(os.path.join(QR_FOLDER,product['style_number']+".png"))
                    cur.execute("INSERT INTO products(retail_customer_price, selling_unit_quantity,manufacturer,material_class,style_number,style_name,cost,options,last_updated) VALUES(%s, %s,%s, %s, %s,%s, %s,%s, %s)", (product['retail_price_override'],product['selling_unit_quantity'],product['manufacturer'],product['material_class'],product['style_number'],product['style_name'],product['cost'],None,None))
                    mysql.connection.commit()
                else:
                    return "Invalid Data"
        return "True"
    elif filename.endswith(".xlsx"):
        
        # Read and store content
        # of an excel file 
        read_file = pd.read_excel (os.path.join(UPLOAD_FOLDER,filename))
        
        # Write the dataframe object
        # into csv file
        csv_filename = filename.replace(".xlsx",".csv")
        read_file.to_csv (os.path.join(UPLOAD_FOLDER,csv_filename), 
                        index = None,
                        header=True)
        # now the same code above as csv 

        with open(os.path.join(UPLOAD_FOLDER,csv_filename), 'r') as f:
            # Read the CSV file
            reader = csv.reader(f)

            # Get the headers from the first line
            headers = next(reader)

            # Initialize an empty list to store the product data
            products = []

            # Iterate through the rows
            for row in reader:
                # Create a dictionary for the product data
                product = {}

                # Map the headers to the values
                for i, header in enumerate(headers):
                    product[header] = row[i]

                    # Add the product data to the list
                    # products.append(product)

                # return product
                if "cost" in product and "style_number" in product and "style_name" in product and "retail_price_override" in product and "manufacturer" in product and "selling_unit_quantity" in product:
                    qr_code = qrcode.make('/view-product-by-style-number/'+product['style_number'])
                    # Save image to a file
                    qr_code.save(os.path.join(QR_FOLDER,product['style_number']+".png"))
                    cur = mysql.connection.cursor()
                    cur.execute("INSERT INTO products(retail_customer_price, selling_unit_quantity,manufacturer,material_class,style_number,style_name,cost,options,last_updated) VALUES(%s, %s,%s, %s, %s,%s, %s,%s, %s)", (product['retail_price_override'],product['selling_unit_quantity'],product['manufacturer'],product['material_class'],product['style_number'],product['style_name'],product['cost'],None,None))
                    mysql.connection.commit()
                else:
                    return "Invalid Data"
        return "True"
        # --xx-xx--

