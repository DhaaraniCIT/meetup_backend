import flask
import sys
from flask import Flask,request,render_template,jsonify,json
from flask_cors import CORS
import hashlib 
import math, random
import MySQLdb
from captcha.image import ImageCaptcha
import base64 

app = flask.Flask(__name__)
CORS(app)
app.config["DEBUG"] = True

hostname = "localhost"
username = "root"
password = ""
database = "meetup"

@app.route('/captcha', methods =['GET'])
def captcha():
    n1=6
    digits = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789abcdefghijklmnopqrstuvwxyz"
    cap = "" 
    for i in range(n1) : 
        cap += digits[math.floor(random.random() * len(digits))]

    image = ImageCaptcha(width = 280, height = 90)
    data = image.generate(cap)
    image.write(cap, 'captcha.png')
    with open("captcha.png", "rb") as img_file:
        ing = base64.b64encode(img_file.read()).decode('utf-8')
    # print(ing)
    return jsonify({"data":cap,"img":ing})


#login Module
@app.route('/login', methods=['POST']) 
def login():
    content = request.get_json()
    hashpassword = hashlib.md5(content['password'].encode())
    conn = MySQLdb.connect(hostname,username,password,database)
    cur = conn.cursor()
    sql = 'SELECT * FROM user WHERE email= "'+content['email']+'" AND password = "'+hashpassword.hexdigest()+'"'        
    cur.execute(sql)
    account = cur.fetchone()
    conn.close()
    print(account)
    if account:
        keys=('userId','name','email','token','profilePicture')
        account=list(account)
        account.pop(5)
        account=tuple(account)
        users={}
        user = dict(zip(keys,account))
        return jsonify({"data":user})
    else:
        return jsonify("error")

@app.route('/signup', methods =['POST'])
def signup():
    content = request.get_json()
    print(request.get_json(),content['email'])
    conn = MySQLdb.connect(hostname,username,password,database)
    cur = conn.cursor()
    sql = 'SELECT * FROM user WHERE email= "'+content['email']+'"'        
    cur.execute(sql)
    account = cur.fetchone()
    print(account)
    if account:
        return jsonify({"error":"User Already Exist with this email"})
    else:
        if content['recaptcha']==content['captcha']:
            n1=50
            n2=100
            digits = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789abcdefghijklmnopqrstuvwxyz"
            key = "" 
            link=""
            for i in range(n2) : 
                key += digits[math.floor(random.random() * len(digits))] 
            for i in range(n1) : 
                link += digits[math.floor(random.random() * len(digits))]
            n=1
            digits = "12345678"
            pic = random.randint(1,8)

            hashpassword = hashlib.md5(content['password'].encode())
            cur = conn.cursor()            
            sql = "INSERT INTO user (name, email, password,APIkey,profilePic) VALUES ('" + content['name'] + "','" + content['email'] + "','" + hashpassword.hexdigest() + "','"+key+"',"+str(pic)+")"
            print(sql)
            cur = conn.cursor()
            cur.execute(sql)
            conn.commit()
            cur = conn.cursor()
            sql = 'SELECT * FROM user ORDER BY userId DESC LIMIT 1'        
            cur.execute(sql)
            account = cur.fetchone()
            keys=('userId','name','email','token','profilePictureURL')
            print(account)
            account=list(account)
            account.pop(5)
            account=tuple(account)
            user={}
            user = dict(zip(keys,account))
            return jsonify({"data":user})
        else:
            return jsonify({"error":"CAPTCHA is incorrect"})

@app.route('/viewUser/<int:id>', methods =['GET'])
def viewUser(id):
    conn = MySQLdb.connect(hostname,username,password,database)
    cur = conn.cursor()
    sql = 'SELECT * FROM user WHERE userId='+str(id);      
    cur.execute(sql)
    account = cur.fetchone()
    keys=('userId','name','email','token','profilePicture')
    # print(account)
    account=list(account)
    account.pop(4)
    account=tuple(account)
    user={}
    user = dict(zip(keys,account))
    return jsonify({"data":user})

@app.route('/allEvents', methods =['GET'])
def viewevents():
    conn = MySQLdb.connect(hostname,username,password,database)
    sql = 'SELECT * FROM events'
    print(sql)
    cur = conn.cursor()
    cur.execute(sql)
    result = cur.fetchall()
    length = len(result)
    if length >=0 :
        event=[]
        for x in range(length):
            keys=('eventId','Ename','description','Edomine','Ecity','Edata','tickets','Eprice','TicBooked')
            account=list(result[x])
            account=tuple(account)
            user={}
            user = dict(zip(keys,account))
            event.append(user)
        return jsonify({"data":event})
    else:
        return jsonify({"error":"Somthing Went Worng"})

@app.route('/userEvents/<int:id>', methods =['GET'])
def getUserevents(id):
    conn = MySQLdb.connect(hostname,username,password,database)
    sql = 'SELECT * FROM booking WHERE userId = '+str(id)
    print(sql)
    cur = conn.cursor()
    cur.execute(sql)
    result = cur.fetchall()
    length = len(result)
    if length >=0 :
        event=[]
        for x in range(length):
            keys=('transId','userId','EventId','date')
            account=list(result[x])
            account=tuple(account)
            user={}
            user = dict(zip(keys,account))
            event.append(user)
        return jsonify({"data":event})
    else:
        return jsonify({"error":"Somthing Went Worng"})

@app.route('/addEvent', methods =['POST'])
def addevent():
    content = request.get_json()
    conn = MySQLdb.connect(hostname,username,password,database)
    sql = "INSERT INTO events (Ename, description, Edomine, Ecity, Edate, tickets, Eprice, TicBooked) VALUES ('" + content['name'] + "','" + content['des'] + "','" + content['domin'] + "','"+content['city']+"','"+content['date']+"',"+str(content['tickets'])+","+str(content['price'])+","+str(0)+")"
    print(sql)
    cur = conn.cursor()
    c = cur.execute(sql)
    conn.commit()
    if(c):
        return jsonify({"data":"success"})
    else:
        return jsonify({"error":"failer"})

@app.route('/booking', methods =['POST'])
def bookevent():
    content = request.get_json()
    conn = MySQLdb.connect(hostname,username,password,database)
    sql = "INSERT INTO booking (userId, EventId, TransDate) VALUES (" + str(content['userId']) + ","+str(content['EventId'])+",'"+content['date']+"')"
    print(sql)
    cur = conn.cursor()
    c = cur.execute(sql)
    conn.commit()
    sql = "SELECT TicBooked from events where eventId="+str(content['EventId'])
    cur = conn.cursor()
    c = cur.execute(sql)
    count = cur.fetchone()
    counts = int(count[0])+1
    sql = "UPDATE events SET TicBooked ='"+str(counts)+"' where eventId='"+str(content['EventId'])+"'"
    print(sql)
    cur = conn.cursor()
    c = cur.execute(sql)
    conn.commit()
    print(c)
    if(c):
        return jsonify({"data":"success"})
    else:
        return jsonify({"error":"failer"})

@app.route('/cancelEvents/<int:id>', methods =['DELETE'])
def deleteEvenet(id):
    print(id)
    conn = MySQLdb.connect(hostname,username,password,database)
    cur = conn.cursor()
    cur.execute( "select * FROM booking WHERE TransId="+str(id) )
    cancel = cur.fetchone()
    exe = cur.execute( "DELETE FROM booking WHERE TransId="+str(id) )
    if exe > 0:
        conn.commit()
        sql = "SELECT TicBooked from events where eventId="+str(cancel[2])
        print(sql)
        cur = conn.cursor()
        c = cur.execute(sql)
        count = cur.fetchone()
        counts = int(count[0])-1
        sql = "UPDATE events SET TicBooked ='"+str(counts)+"' where eventId='"+str(cancel[2])+"'"
        print(sql)
        cur = conn.cursor()
        c = cur.execute(sql)
        conn.commit()
        # print(exe)
        return jsonify({"data":"Deletion is successful"})
    else:
        return jsonify({"error":"Deletion is unsuccessful"})

if __name__=='__main__':
	 app.run(debug=True)  