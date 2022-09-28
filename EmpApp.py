from crypt import methods
import email
import re
from unicodedata import name
from flask import Flask, render_template, request, redirect, session, flash, url_for
from pymysql import connections
import os
import boto3
from config import *
from datetime import datetime
from flask_session import Session

app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# For Flash #
app.secret_key = "secret" 

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
attendance_id = 1

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

@app.route("/viewEmployee", methods=['GET', 'POST'])
def viewEmployee():
    emp_id = request.form['empId']
    
    sql_query = "SELECT * FROM employee WHERE emp_id = '" + emp_id + "'"
    cursor = db_conn.cursor()
    try: 
        cursor.execute(sql_query)
        employee = list(cursor.fetchone())
        cursor.close()
        return render_template('viewemployee.html', employee = employee)
    except Exception as e:
        return str(e)

@app.route("/updateEmployee", methods=['GET', 'POST'])
def updateEmployee():
    emp_id = request.form['empId']

    sql_query = "SELECT * FROM employee WHERE emp_id = '" + emp_id + "'"
    cursor = db_conn.cursor()
    try: 
        cursor.execute(sql_query)
        employee = list(cursor.fetchone())
        cursor.close()
        return render_template('updateemployee.html', employee = employee)
    except Exception as e:
        return str(e)

@app.route("/updateEmp", methods=['GET','POST'])
def updateEmp():
    emp_id = request.form['empId']
    name = request.form['empName']
    email = request.form['email']
    password = request.form['password']
    phoneNumber = request.form['phoneNumber']
    pri_skill = request.form['pri_skill']
    location =  request.form['location']

    update_sql = "UPDATE employee SET  name ='" + name + "', email ='" + email + "', password ='" + password + "', phoneNumber ='" + phoneNumber + "', pri_skill ='" + pri_skill + "', location ='" + location + "' WHERE emp_id ='" + emp_id + "'"
    cursor = db_conn.cursor()

    try:
        cursor.execute(update_sql)
        db_conn.commit()
    finally:
        cursor.close()

    print("all modification done...")
    return redirect(url_for('employee'))

@app.route("/deleteEmployee", methods=['GET', 'POST'])
def deleteEmployee():
    emp_id = request.form['empId']

    sql_query = "SELECT * FROM employee WHERE emp_id = '" + emp_id + "'"
    cursor = db_conn.cursor()
    try: 
        cursor.execute(sql_query)
        employee = list(cursor.fetchone())
        cursor.close()
        return render_template('employee.html', employee = employee)
    except Exception as e:
        return str(e)

@app.route("/deleteEmp", methods=['GET','POST'])
def deleteEmp():
        emp_id = request.form['empId']

        sql_query = "DELETE FROM employee WHERE emp_id = '" + emp_id + "'"
        cursor = db_conn.cursor()

        try:
            cursor.execute(sql_query)
            db_conn.commit()
            cursor.close()
            return render_template('employee.html')
        except Exception as e:
            return str(e)

@app.route("/attendance", methods=['GET','POST'])
def Attendance():
    sql_query = "SELECT * FROM attendance"
    cursor = db_conn.cursor()
    try: 
        # Extract employee records #
        cursor.execute(sql_query)
        records = list(cursor.fetchall())

        # Put records into an employee list & Convert rows inside records from tuple to list#
        attendances = []
        for rows in records:
            attendances.append(list(rows))

        cursor.close()
        return render_template('attendance.html', attendances = attendances)
    except Exception as e:
        return str(e)

@app.route("/addAttendance", methods=['GET', 'POST'])
def addAttendance():
    emp_id = session['id']
    
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
    emp_id = session["id"]
    name = session["name"]

    today = datetime.today()
    date = today.strftime("%d/%m/%Y")
    check_in = today.strftime("%X")
    date = str(date)
    check_in = str(check_in)

    insert_sql = "INSERT INTO attendance (emp_id, name, date, check_in) VALUES (%s, %s, %s, %s)"
    cursor = db_conn.cursor()

    try:
        cursor.execute(insert_sql, (emp_id, name, date, check_in))
        db_conn.commit()
    finally:
        cursor.close()

    print("all modification done...")
    return render_template('index.html')

@app.route("/updateAttendance", methods=['GET', 'POST'])
def updateAttendance():
    att_id = request.form['attId']

    sql_query = "SELECT * FROM attendance WHERE att_id = '" + att_id + "'"
    cursor = db_conn.cursor()
    try: 
        cursor.execute(sql_query)
        attendance = list(cursor.fetchone())
        cursor.close()
        return render_template('updateattendance.html', attendance = attendance)
    except Exception as e:
        return str(e)

@app.route("/updateAtt", methods=['GET','POST'])
def updateAtt():
    att_id = request.form['attId']
    emp_id = request.form['empId']
    name = request.form['empName']
    date = request.form['date']
    check_in = request.form['checkIn']

    today = datetime.now()
    check_out = today.strftime("%X")
    check_out = str(check_out)
    print(check_out)

    update_sql = "UPDATE attendance SET emp_id ='" + emp_id + "', name ='" + name + "', date ='" + date + "', check_in ='" + check_in + "', check_out ='" + check_out + "' WHERE att_id ='" + att_id + "'"
    cursor = db_conn.cursor()

    try:
        cursor.execute(update_sql)
        db_conn.commit()
    finally:
        cursor.close()

    print("all modification done...")
    return redirect(url_for('Attendance'))

@app.route("/deleteAttendance", methods=['GET', 'POST'])
def deleteAttendance():
    att_id = request.form['attId']

    sql_query = "SELECT * FROM attendance WHERE att_id = '" + att_id + "'"
    cursor = db_conn.cursor()
    try: 
        cursor.execute(sql_query)
        attendance = list(cursor.fetchone())
        cursor.close()
        return render_template('attendance.html', attendance = attendance)
    except Exception as e:
        return str(e)

@app.route("/deleteAtt", methods=['GET','POST'])
def deleteAtt():

        att_id = request.form['attId']

        sql_query = "DELETE FROM attendance WHERE att_id = '" + att_id + "'"
        cursor = db_conn.cursor()

        try:
            cursor.execute(sql_query)
            db_conn.commit()
            cursor.close()
            return render_template('attendance.html')
        except Exception as e:
            return str(e)

@app.route("/viewAttendance", methods=['GET', 'POST'])
def viewAttendance():
    att_id = request.form['attId']

    sql_query = "SELECT * FROM attendance WHERE att_id = '" + att_id + "'"
    cursor = db_conn.cursor()
    try: 
        cursor.execute(sql_query)
        attendance = list(cursor.fetchone())
        cursor.close()
        return render_template('attendance.html', attendance = attendance)
    except Exception as e:
        return str(e)            

@app.route("/login", methods=['GET', 'POST'])
def login():
      # if form is submited
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        sql_query = "SELECT * FROM employee WHERE email ='" + email + "'"
        cursor = db_conn.cursor()
        try:
            cursor.execute(sql_query)
            row = cursor.fetchone()
            if row != None and row[3] == password:
                # record the user name
                session["id"] = row[0]
                session["name"] = row[1]
                cursor.close()
                # redirect to the main page
                return redirect("/")
            else:
                flash("Invalid email or password. Please try again.")
        except Exception as e:
            return str(e)
    return render_template('login.html')



@app.route("/logout")
def logout():
    session["id"] = None
    session["name"] = None
    return redirect("/")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
