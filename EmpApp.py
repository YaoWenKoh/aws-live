from crypt import methods
from unicodedata import name
from flask import Flask, render_template, request
from pymysql import connections
import os
import boto3
from config import *
from datetime import datetime

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

@app.route("/employee", methods=['GET','POST'])
def employee():
    sql_query = "SELECT * FROM employee"
    cursor = db_conn.cursor()
    try: 
        # Extract employee records #
        cursor.execute(sql_query)
        records = list(cursor.fetchall())

        # Put records into an employee list & Convert rows inside records from tuple to list#
        employees = []
        for rows in records:
            employees.append(list(rows))

        cursor.close()
        return render_template('employee.html', employees = employees)
    except Exception as e:
        return str(e)
        
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

@app.route("/addemp", methods=['GET','POST'])
def AddEmp():
    emp_id = request.form['empId']
    name = request.form['empName']
    email = request.form["empEmail"]
    password = request.form["empPassword"]
    phone_number = request.form["empPhoneNumber"]
    pri_skill = request.form['empPriSkill']
    location = request.form['empLocation']

    insert_sql = "INSERT INTO employee VALUES (%s, %s, %s, %s, %s, %s, %s)"
    cursor = db_conn.cursor()

    try:
        cursor.execute(insert_sql, (emp_id, name, email, password, phone_number, pri_skill, location))
        db_conn.commit()
    finally:
        cursor.close()

    print("all modification done...")
    return render_template('index.html')

@app.route("/attendance", methods=['GET','POST'])
def Attendance():
    sql_query = "SELECT * FROM employee"
    cursor = db_conn.cursor()
    try: 
        # Extract employee records #
        cursor.execute(sql_query)
        records = list(cursor.fetchall())

        # Put records into an employee list & Convert rows inside records from tuple to list#
        employees = []
        for rows in records:
            employees.append(list(rows))

        cursor.close()
        return render_template('attendance.html', employees = employees)
    except Exception as e:
        return str(e)

@app.route("/addAttendance", methods=['GET', 'POST'])
def addAttendance():
    emp_id = request.form['empId']

    sql_query = "SELECT * FROM employee WHERE emp_id = '" + emp_id + "'"
    cursor = db_conn.cursor()
    try: 
        cursor.execute(sql_query)
        employee = list(cursor.fetchone())
        cursor.close()
        return render_template('addattendance.html', employee = employee)
    except Exception as e:
        return str(e)
    
@app.route("/addAtt", methods=['GET','POST'])
def addAtt():

    emp_id = request.form['empId']
    name = request.form['empName']

    today = datetime.today()
    date = today.strftime("%d/%m/%Y")
    check_in = today.strftime("%H:%M:%S")


    insert_sql = "INSERT INTO attendance VALUES (%s, %s, %s, %s)"
    cursor = db_conn.cursor()

    try:
        cursor.execute(insert_sql, (emp_id, name, date, check_in))
        db_conn.commit()
    finally:
        cursor.close()

    print("all modification done...")
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
