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

s3 = boto3.resource('s3')
s3_client = boto3.client('s3')

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

def get_file_extension(filename):
    if '.' in filename:
        return filename.rsplit('.', 1)[1].lower()

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
def addemp():
    emp_id = request.form['empId']
    name = request.form['empName']
    email = request.form["empEmail"]
    password = request.form["empPassword"]
    phone_number = request.form["empPhoneNumber"]
    pri_skill = request.form['empPriSkill']
    location = request.form['empLocation']
    profile = request.files['profile']

    insert_sql = "INSERT INTO employee VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
    cursor = db_conn.cursor()
    
    try:
        image_file_name_in_s3 = "employee/_image_file" + str(emp_id) + get_file_extension(profile.filename)
        cursor.execute(insert_sql, (emp_id, name, email, password, phone_number, pri_skill, location, image_file_name_in_s3))
        db_conn.commit()
        try:
            print("Data inserted in MySQL RDS... uploading image to S3...")
            s3.Bucket(custombucket).put_object(Key=image_file_name_in_s3, Body=profile)
            bucket_location = boto3.client('s3').get_bucket_location(Bucket=custombucket)
            s3_location = (bucket_location['LocationConstraint'])
            if s3_location is None:
                s3_location = ''
            else:
                s3_location = '-' + s3_location
                object_url = "https://s3{0}.amazonaws.com/{1}/{2}".format(
                    s3_location,
                    custombucket,
                    image_file_name_in_s3)
                flash("Profile added successfully!")

        except Exception as e:
                return str(e)

    finally:
        cursor.close()

    print("all modification done...")
    return render_template('employee.html')

@app.route("/viewEmployee", methods=['GET', 'POST'])
def viewEmployee():
    emp_id = request.form['empId']
    
    sql_query = "SELECT * FROM employee WHERE emp_id = '" + emp_id + "'"
    cursor = db_conn.cursor()
    try: 
        cursor.execute(sql_query)
        employee = list(cursor.fetchone())
        public_url = s3_client.generate_presigned_url('get_object', 
                                                                Params = {'Bucket': custombucket, 
                                                                            'Key': employee[7]})

        employee.append(public_url)
        employee.append("checked")

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
            return redirect('/employee')
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
            return redirect('attendance')
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
        return render_template('viewattendance.html', attendance = attendance)
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

@app.route("/portfolio")
def portfolio():

    profile = ["2104900.jpg", "2105038.jpg"]
    picList = []
    # Extract employee cert image #
    for pic in profile:
        public_url = s3_client.generate_presigned_url('get_object', 
                                                        Params = {'Bucket': custombucket, 
                                                                    'Key': pic})
        picList.append(public_url)
    return render_template('portfolio.html', picList = picList)

@app.route("/certificate", methods=['GET','POST'])
def certificate():
    sql_query = "SELECT * FROM certificate WHERE emp_id ='"+ session["id"] +"'"
    cursor = db_conn.cursor()
    try:
        cursor.execute(sql_query)
        records = list(cursor.fetchall())

        certificate = []
        for rows in records:
            certificate.append(list(rows))
        cursor.close()
        return render_template('certificate.html', certificate = certificate)
    except Exception as e:
        return str(e)

@app.route("/viewcertificate", methods=['GET','POST'])
def viewcertificate():
    if request.method == "POST":
        certid = request.form['certId']
        sql_query = "SELECT * FROM certificate WHERE certificateID ='"+ certid +"'"
        cursor = db_conn.cursor()
        try:
            cursor.execute(sql_query)
            cert = list(cursor.fetchone())

            public_url = s3_client.generate_presigned_url('get_object', 
                                                                Params = {'Bucket': custombucket, 
                                                                            'Key': cert[4]})

            cert.append(public_url)
            cert.append("checked")

            cursor.close()

            return render_template('viewcertificate.html', cert = cert)
        except Exception as e:
            return str(e)
    else:
        return redirect("/certificate")

@app.route("/addcertificate", methods=['GET','POST'])
def addcertificate():
    if request.method == "POST":
        cName = request.form.get("certName")
        cDesc = request.form.get("certDesc")
        cDateTime =  str(datetime.now().strftime("%Y-%m-%d"))
        cFile = request.files["myCert"]

        if cFile.filename == "":
            return "Please select a image file"

        sql_query = "SELECT * FROM certificate"
        cursor = db_conn.cursor()
        try:
            cursor.execute(sql_query)
            records = cursor.fetchall()
            cID =  int(len(records)) + 1
        except Exception as e:
            return str(e)

        sql_query = "INSERT INTO certificate VALUES (%s, %s, %s, %s, %s, %s)"

        try:
            image_file_name_in_s3 = "cert/" + str(session["id"]) + "_image_file" + str(cID) + get_file_extension(cFile.filename)
            cursor.execute(sql_query, (cID, cName, cDesc, cDateTime, image_file_name_in_s3, session["id"]))
            db_conn.commit()

            try:
                print("Data inserted in MySQL RDS... uploading image to S3...")
                s3.Bucket(custombucket).put_object(Key=image_file_name_in_s3, Body=cFile)
                bucket_location = boto3.client('s3').get_bucket_location(Bucket=custombucket)
                s3_location = (bucket_location['LocationConstraint'])

                if s3_location is None:
                    s3_location = ''
                else:
                    s3_location = '-' + s3_location

                object_url = "https://s3{0}.amazonaws.com/{1}/{2}".format(
                    s3_location,
                    custombucket,
                    image_file_name_in_s3)

            except Exception as e:
                return str(e)

        except Exception as e:
            return str(e)

        finally:
            cursor.close()
            return redirect("/certificate")

    return render_template('addcertificate.html')

@app.route("/deletecertificate", methods=['GET','POST'])
def deletecertificate():
    if request.method == "POST":
        cID = request.form['certId']
        sql_query = "SELECT * FROM certificate WHERE certificateID ='"+ cID+"'"
        cursor = db_conn.cursor()

        try:
            try:
                cursor.execute(sql_query)
                cert = list(cursor.fetchone())
                s3.Object(custombucket, cert[4]).delete()
            except Exception as e:
                return str(e)
            sql_query = "DELETE FROM certificate WHERE certificateID ='"+ cID+"'"
            cursor.execute(sql_query)
            db_conn.commit
            cursor.close()
            return redirect("/certificate")
        except Exception as e:
            return str(e)
    else:
        return redirect("/certificate")

@app.route("/deletecertificateconfirmation", methods=['GET','POST'])
def deletecertificateconfirmation():
    if request.method == "POST":
        cID = request.form['certId']
        sql_query = "SELECT * FROM certificate WHERE certificateID ='"+ cID+"'"
        cursor = db_conn.cursor()

        try:
            cursor.execute(sql_query)
            cert = list(cursor.fetchone())
            #s3.Object(custombucket, cert[4]).delete()
            public_url = s3_client.generate_presigned_url('get_object', 
                                                                Params = {'Bucket': custombucket, 
                                                                            'Key': cert[4]})
            cert.append(public_url)
            cert.append("checked")
            cursor.close()
            return render_template('deletecertificate.html', cert = cert)
        except Exception as e:
            return str(e)
    else:
        return redirect("/certificate")

@app.route("/modifycertificateconfirmation", methods=['GET','POST'])
def modifycertificateconfirmation():
    if request.method == "POST":
        cID = request.form['certId']
        sql_query = "SELECT * FROM certificate WHERE certificateID ='"+ cID+"'"
        cursor = db_conn.cursor()

        try:
            cursor.execute(sql_query)
            cert = list(cursor.fetchone())
            #s3.Object(custombucket, cert[4]).delete()
            public_url = s3_client.generate_presigned_url('get_object', 
                                                                Params = {'Bucket': custombucket, 
                                                                            'Key': cert[4]})
            cert.append(public_url)
            cert.append("checked")
            cursor.close()
            return render_template('modifycertificate.html', cert = cert)
        except Exception as e:
            return str(e)
    else:
        return redirect("/certificate")

@app.route("/modifycertificate", methods=['GET','POST'])
def modifycertificate():
    if request.method == "POST":
        cID = request.form['certId']
        cName = request.form['certName']
        cDesc = request.form['certDesc']
        cFile = request.files['myCert']
        sql_query = "SELECT * FROM certificate WHERE certificateID ='"+ cID+"'"
        cursor = db_conn.cursor()

        try:
            cursor.execute(sql_query)
            cert = list(cursor.fetchone())
            public_url = s3_client.generate_presigned_url('get_object', 
                                                                Params = {'Bucket': custombucket, 
                                                                            'Key': cert[4]})
            cert.append(public_url)
            cert.append("checked")
        except Exception as e:
            return str(e)
        sql_query = "UPDATE certificate SET certificateName='"+ cName +"', certificateDesc='"+ cDesc+"' WHERE emp_id='"+ session["id"] +"' and certificateID='"+ cID+"'"
        if(cFile.filename != ""):
            try:
                cursor.execute(sql_query)
                db_conn.commit()
                try:
                    s3.Object(custombucket, cert[4]).delete()
                    print("Data inserted in MySQL RDS... uploading image to S3...")
                    s3.Bucket(custombucket).put_object(Key=cert[4], Body=cFile)
                    bucket_location = boto3.client('s3').get_bucket_location(Bucket=custombucket)
                    s3_location = (bucket_location['LocationConstraint'])

                    if s3_location is None:
                        s3_location = ''
                    else:
                        s3_location = '-' + s3_location

                    object_url = "https://s3{0}.amazonaws.com/{1}/{2}".format(
                        s3_location,
                        custombucket,
                        cert[4])

                    flash("Certificate added successfully!")

                except Exception as e:
                    return str(e)
            except Exception as e:
                return str(e)
        else:
            cursor.execute(sql_query)
            db_conn.commit()

        cursor.close()
        return redirect("/certificate")
    else:
        return redirect("/certificate")

@app.route("/addemp", methods=['POST'])
def AddEmp():
    emp_id = request.form['emp_id']
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    pri_skill = request.form['pri_skill']
    location = request.form['location']
    emp_image_file = request.files['emp_image_file']

    insert_sql = "INSERT INTO employee VALUES (%s, %s, %s, %s, %s)"
    cursor = db_conn.cursor()

    if emp_image_file.filename == "":
        return "Please select a file"

    try:

        cursor.execute(insert_sql, (emp_id, first_name, last_name, pri_skill, location))
        db_conn.commit()
        emp_name = "" + first_name + " " + last_name
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
    return render_template('AddEmpOutput.html', name=emp_name)

@app.route("/performancenote", methods=['GET','POST'])
def performancenote():
    sql_query = "SELECT * FROM performanceNote"
    cursor = db_conn.cursor()
    try:
        cursor.execute(sql_query)
        records = list(cursor.fetchall())

        pn = []
        for rows in records:
            pn.append(list(rows))
        cursor.close()
        return render_template('performancenote.html', pn = pn)
    except Exception as e:
        return str(e)

@app.route("/addperformancenote", methods=['GET','POST'])
def addperformancenote():
    if request.method == "POST":
        pnTitle = request.form.get("pnTitle")
        pnDesc = request.form.get("pnDesc")
        pnDateTime =  str(datetime.now().strftime("%Y-%m-%d"))
        pnOwner = request.form.get("empId")

        sql_query = "SELECT * FROM performanceNote"
        cursor = db_conn.cursor()
        try:
            cursor.execute(sql_query)
            records = cursor.fetchall()
            cursor.close()
            pnID =  int(len(records)) + 1
        except Exception as e:
            return str(e)
        sql_query = "INSERT INTO performanceNote VALUES (%s, %s, %s, %s, %s)"
        cursor = db_conn.cursor()
        try:
            cursor.execute(sql_query, (pnID, pnTitle, pnDesc, pnDateTime, pnOwner))
            db_conn.commit()
            print("checkpoint1")
        except Exception as e:
            return str(e)

        finally:
            cursor.close()
            return redirect("/performancenote")
    else:
        sql_query = "SELECT * FROM employee"
        cursor = db_conn.cursor()
        cursor.execute(sql_query)
        records = cursor.fetchall()
        cursor.close()
        return render_template('addperformancenote.html', employees = records)

@app.route("/deleteperformancenote", methods=['GET','POST'])
def deleteperformancenote():
    if request.method == "POST":
        pnID = request.form['pnId']
        sql_query = "DELETE FROM performanceNote WHERE pnID ='"+ pnID+"'"
        cursor = db_conn.cursor()

        try:
            cursor.execute(sql_query)
            db_conn.commit
            cursor.close()
            return redirect("/performancenote")
        except Exception as e:
            return str(e)
    else:
        return redirect("/performancenote")

@app.route("/deleteperformancenoteconfirmation", methods=['GET','POST'])
def deleteperformancenoteconfirmation():
    if request.method == "POST":
        pnID = request.form['pnId']
        sql_query = "SELECT * FROM performanceNote WHERE pnID ='"+ pnID+"'"
        cursor = db_conn.cursor()

        try:
            cursor.execute(sql_query)
            record = list(cursor.fetchone())

            sql_query = "SELECT * FROM employee WHERE emp_id='"+ record[4] +"'"
            cursor.execute(sql_query)
            employee = list(cursor.fetchone())

            cursor.close()
            return render_template('deleteperformancenote.html', pn = record, employee = employee)
        except Exception as e:
            return str(e)
    else:
        return redirect("/performancenote")

@app.route("/logout")
def logout():
    session["id"] = None
    session["name"] = None
    return redirect("/")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
