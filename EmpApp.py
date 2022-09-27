from crypt import methods
from flask import Flask, render_template, request
from pymysql import connections
import os
import boto3
from config import *

app = Flask(__name__)

bucket = custombucket
region = customregion

db_conn = connections.Connection(
    host=customhost,
    port=3306,
    user=customuser,
    password=custompass,
    db=customdb

)
output = {}
table = 'employee'

employee_id = 1001


@app.route("/", methods=['GET', 'POST'])
def home():
    return render_template('index.html')

@app.route("/about", methods=['POST'])
def about():
    return render_template('www.intellipaat.com')

@app.route("/addEmployee", methods=['GET', 'POST'])
def addEmployee():
    # Setting employee id automatically #
    sql_query = "SELECT * FROM employee"
    cursor = db_conn.cursor()
    try: 
        cursor.execute(sql_query)
        records = cursor.fetchall()
        emp_id = employee_id + int(len(records))
        cursor.close()
        return render_template('AddEmp.html', empId = emp_id)
    except Exception as e:
        return str(e)

@app.route("/addemp", methods=['POST'])
def AddEmp():
    emp_id = request.form['empId']
    name = request.form['name']
    email = request.form["email"]
    password = request.form["password"]
    phone_number = request.form["phone_number"]
    pri_skill = request.form['pri_skill']
    location = request.form['location']
    emp_image_file = request.files['emp_image_file']

    insert_sql = "INSERT INTO employee VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
    cursor = db_conn.cursor()

    if emp_image_file.filename == "":
        return "Please select a file"

    try:

        cursor.execute(insert_sql, (emp_id, name, email, password, phone_number, pri_skill, location))
        db_conn.commit()
        # Uplaod image file in S3 #
        emp_image_file_name_in_s3 = "emp-id-" + str(emp_id) + "_image_file"
        s3 = boto3.resource('s3')

        try:
            print("Data inserted in MySQL RDS... uploading image to S3...")
            s3.Bucket(custombucket).put_object(Key=emp_image_file_name_in_s3, Body=emp_image_file)
            bucket_location = boto3.client('s3').get_bucket_location(Bucket=custombucket)
            s3_location = (bucket_location['LocationConstraint'])

            if s3_location is None:
                s3_location = ''
            else:
                s3_location = '-' + s3_location

            object_url = "https://s3{0}.amazonaws.com/{1}/{2}".format(
                s3_location,
                custombucket,
                emp_image_file_name_in_s3)

        except Exception as e:
            return str(e)

    finally:
        cursor.close()

    print("all modification done...")
    return render_template('index.html')

@app.route("/addatt", methods=['GET', 'POST'])
def Login():
    return render_template('addAttandance.html')

@app.route("/register", methods=['POST'])
def Register():
    email = request.form['email']
    password = request.form['password']

    insert_sql = "INSERT INTO test VALUES (%s, %s)"
    cursor = db_conn.cursor()
    try:

        cursor.execute(insert_sql, (email,password))
        db_conn.commit()
        object_url = "https://s3{0}.amazonaws.com/{1}/{2}".format(
                custombucket)

    finally:
        cursor.close()

    print("all modification done...")
    return render_template('test.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
