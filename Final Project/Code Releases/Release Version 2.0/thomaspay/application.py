import now as now
from flask import Flask, render_template, request, session
import mysql.connector
import hashlib
import datetime
import os

#db = mysql.connector.connect(user='root', password='root', host='127.0.0.1', database='thomaspay')
db = mysql.connector.connect(user='root', password='root-123', host='thomaspay.clp7fwlohsdk.us-east-2.rds.amazonaws.com', database='thomaspay')

print ('---' + str(db))
cursor = db.cursor()  # create a new cursor for establishing the query

application = app = Flask(__name__)
app.secret_key = os.urandom(24)


@app.route('/')
def hello_world():
    return render_template('index.html')

@app.route('/login', methods=['POST', 'GET'])
def login():
    username = request.form['username']
    password = request.form['password']
    dk = hashlib.pbkdf2_hmac('SHA256', password, b'salt', 100000).encode('base64').strip()
    print(len(dk))
    query = "select count(*) from thomaspay.users where username = '" + str(username) + "' and password = '" + dk + "'"
    print (query)
    cursor.execute(query)
    data = cursor.fetchall()
    print(data)
    if data[0][0] != 0:
        session['user'] = username
        print session['user']
        query1 = "select balance from thomaspay.wallet,thomaspay.users " \
                 "where thomaspay.users.username='" + session['user'] + "' and thomaspay.users.user_id = thomaspay.wallet.user_id"
        print(query1)
        cursor.execute(query1)
        data1 = cursor.fetchall()
        print(data1)
        return render_template('homepage.html', data1=data1)
    else:
        return render_template('index.html')

@app.route('/addbeneficiaryhome', methods = ['POST','GET'])
def addbeneficiaryhome():
    return render_template('addbeneficiary.html')

@app.route('/addbeneficiary', methods = ['POST','GET'])
def addbeneficiary():
    if request.method=='POST':
        nickname = request.form['nickname']
        email = request.form['email']

        #getting the user_id of beneficiary
        query1 = "SELECT user_id from thomaspay.users WHERE user_emailid = '"+str(email)+"'"
        print(query1)
        cursor.execute(query1)
        bef_userid = cursor.fetchall()
        print(bef_userid)

        #Getting the user id of current logged in user
        query2 ="Select user_id from thomaspay.users WHERE username =  '"+session['user']+"' "
        print(query2)
        cursor.execute(query2)
        userid = cursor.fetchall()
        user_mod = userid[0][0]
        #print(user_mod)

        #If beneficiary is not found
        if not bef_userid:
            result = "User Does not exist"
            return render_template('/addbeneficiary.html', result=result)
        #If user tries to add himself
        elif user_mod==bef_userid[0][0]:
            result = "You cannot add yourself as beneficiary"
            return render_template('/addbeneficiary.html', result=result)
        else:
            query = "INSERT into thomaspay.beneficiary ( user_id, beneficiary_id, nickname, email_id)"\
                    "VALUES (%s,%s,%s,%s)"
            val1 = (user_mod,int(bef_userid[0][0]),nickname,email)

            cursor.execute(query,val1)

            db.commit()

            #print(query)

            result = "Beneficiary added Successfuly."
            return render_template('/addbeneficiary.html',result=result)


@app.route('/addmoney', methods=['POST', 'GET'])
def addmoney():
    query = "SELECT card_name,cardnumber FROM thomaspay.account,thomaspay.users " \
            "where thomaspay.users.username='" + session['user'] + "' and thomaspay.users.user_id = thomaspay.account.user_id"
    print(query)
    cursor.execute(query)
    data = cursor.fetchall()
    print(data)
    return render_template('addmoney.html', data=data)


@app.route('/addmoneytodb', methods=['POST', 'GET'])
def addmoneytodb():
    money = request.form['money']
    money1 = float(money)

    query = "SELECT card_name,cardnumber FROM thomaspay.account,thomaspay.users " \
            "where thomaspay.users.username='" + session['user'] + "' and thomaspay.users.user_id = thomaspay.account.user_id"
    print(query)
    cursor.execute(query)
    data = cursor.fetchall()
    if money1 < 0:
        print("i am here")
        message = "Enter valid amount"
        return render_template('addmoney.html', data=data, message=message)
    else:
        print(money1)
        now = datetime.datetime.now()
        date = now.strftime("%Y-%m-%d")
        query0 = "select thomaspay.users.user_id, thomaspay.wallet.balance from thomaspay.wallet, thomaspay.users where thomaspay.users.user_id = thomaspay.wallet.user_id " \
                 "and thomaspay.users.username='" + session['user'] + "'"
        cursor.execute(query0)
        datas = cursor.fetchall()
        uid = datas[0][0]
        balance = datas[0][1]
        print(query0)
        print(balance)
        currentbalance = float(balance)
        updatedbalance = money1 + currentbalance
        print("updated Balance = " + str(updatedbalance))
        query2 = "UPDATE thomaspay.wallet SET balance = %s WHERE user_id = %s"
        val3 = (int(updatedbalance), int(uid))
        cursor.execute(query2, val3)

        query1 = "insert into thomaspay.transactions(user_id, transaction_type, amount, transaction_date, sendto, receivedfrom) " \
                 "values(%s, %s, %s, %s, %s, %s)"
        val1 = (int(uid), 'Credit', float(money1), date, 'null', 'Wallet Updated')
        cursor.execute(query1, val1)

        db.commit()
        print('money updated in db')
        message = "Money successfully added to your wallet !!"

    return render_template('addmoney.html', data=data, message=message)


@app.route('/homepage', methods=['POST', 'GET'])
def homepage():
    query1 = "select balance from thomaspay.wallet,thomaspay.users " \
             "where thomaspay.users.username='" + session['user'] + "' and thomaspay.users.user_id = thomaspay.wallet.user_id"
    print(query1)
    cursor.execute(query1)
    data1 = cursor.fetchall()
    print(data1)
    return render_template('homepage.html', data1=data1)


@app.route('/logout')
def logout():
    session.pop('user', None)
    return render_template('index.html')



@app.route('/viewtransaction', methods=['POST', 'GET'])
def viewtransaction():
    return render_template('viewtransactions.html')


@app.route('/transactions', methods=['POST', 'GET'])
def transations():
    results = []
    periodfrom = request.form['periodfrom']
    periodto = request.form['periodto']
    query = "SELECT transaction_id,transaction_date,transaction_type,sendto,receivedfrom,amount FROM thomaspay.transactions,thomaspay.users " \
            "where users.username='" + session['user'] + "' and thomaspay.users.user_id = thomaspay.transactions.user_id and transaction_date between '" + str(
        periodfrom) + "' and '" + str(periodto) + "'"
    cursor.execute(query)
    data = cursor.fetchall()
    for row in data:
        p = [row[0], str(row[1]), str(row[2])]
        if row[2] == 'Credit':
            p.append(str(row[4]))
        elif row[2] == 'Debit':
            p.append(str(row[3]))
        p.append(row[5])
        results.append(p)
    print(results)

    return render_template('viewtransactions.html', results=results)


# link account
@app.route('/linkaccount', methods=['POST', 'GET'])
def linkaccount():
    return render_template('linkaccount.html')


@app.route('/linkacc', methods=['POST', 'GET'])
def linkacc():
    card_type = str(request.form['card_type'])
    card_number = str(request.form['card_number'])
    cvv_number = str(request.form['cvv_number'])
    month_year = str(request.form['month'])
    x = month_year.split("-")
    now = datetime.datetime.now()
    date = now.strftime("%Y-%m")
    current = date.split("-")
    if x[0] > current[0] or (x[0] == current[0] and (x[1] >= current[1])):
        query1 = "select user_id from thomaspay.users where username='" + session[
            'user'] + "'"
        print(query1)
        cursor.execute(query1)
        uid = cursor.fetchall()
        print(uid[0][0])
        print(type(card_number), type(card_type), type(cvv_number), type(x[0]), type(x[1]), type(uid[0][0]))

        query = "insert into thomaspay.account(user_id, card_name, cardnumber, cvv, month, year) values(%s, %s, %s, %s, %s, %s)"
        val = (int(uid[0][0]), card_type, card_number, cvv_number, x[1], x[0])
        print (query)
        cursor.execute(query, val)
        db.commit()
        message = "Card  Details Entered !!!!!!!!!!!!!!!!!!!!"
    else:
        message = "Card Expired !!!!!!!!!!!!!!!!"
    return render_template('linkaccount.html', message=message)


# quickpay
@app.route('/quickpay', methods=['POST', 'GET'])
def quickpay():
    beneficiaries = getBeneficiaries()
    accounts = getAccounts()
    return render_template('quickpay.html', beneficiaries=beneficiaries, accounts=accounts)


@app.route('/getBeneficiaries', methods=['POST', 'GET'])
def getBeneficiaries():
    query1 = "select beneficiary_id, nickname from thomaspay.beneficiary, thomaspay.users " \
             "where thomaspay.beneficiary.user_id=thomaspay.users.user_id and thomaspay.users.username = '" + session['user'] + "'"
    print(query1)
    cursor.execute(query1)
    results = cursor.fetchall()
    print(results)
    return results


@app.route('/getAccounts', methods=['POST', 'GET'])
def getAccounts():
    query1 = "select account_id, cardnumber, card_name from thomaspay.account, thomaspay.users " \
             "where thomaspay.account.user_id=thomaspay.users.user_id and thomaspay.users.username = '" + session['user'] + "'"
    print(query1)
    cursor.execute(query1)
    results = cursor.fetchall()
    print(results)
    return results


@app.route('/quickpayamount', methods=['POST', 'GET'])
def quickpayamount():
    print('testing')
    beneficiaries = getBeneficiaries()
    accounts = getAccounts()
    now = datetime.datetime.now()
    date = now.strftime("%Y-%m-%d")
    beneficiary = str(request.form['beneficiary'])
    amount = int(request.form['amount'])
    query0 = "select thomaspay.users.user_id, thomaspay.wallet.balance from thomaspay.wallet, thomaspay.users where thomaspay.users.user_id = thomaspay.wallet.user_id " \
             "and thomaspay.users.username='" + session['user'] + "'"
    cursor.execute(query0)
    data = cursor.fetchall()
    uid = data[0][0]
    balance = data[0][1]
    print(uid)
    print("test" + str(amount))
    print(date, beneficiary, amount)
    if balance >= amount:
        query11 = "select nickname from thomaspay.beneficiary where beneficiary_id = %s and user_id = %s"
        val11 = (int(beneficiary), int(uid))
        cursor.execute(query11, val11)
        nickname = cursor.fetchall()
        print(nickname[0][0])
        query1 = "insert into thomaspay.transactions(user_id, transaction_type, amount, transaction_date, sendto, receivedfrom) " \
                 "values(%s, %s, %s, %s, %s, %s)"
        val1 = (int(uid), 'Debit', float(amount), date, nickname[0][0], 'null')
        val2 = (beneficiary, 'Credit', float(amount), date, 'null', session['user'])
        cursor.execute(query1, val1)
        cursor.execute(query1, val2)
        query2 = "UPDATE thomaspay.wallet SET balance = balance - %s WHERE user_id = %s and balance >= balance - %s"
        val3 = (float(amount), int(uid), float(amount))
        cursor.execute(query2, val3)
        query3 = "UPDATE thomaspay.wallet SET balance = balance + %s WHERE user_id = %s and balance >= balance - %s"
        val4 = (float(amount), int(beneficiary), float(amount))
        cursor.execute(query3, val4)
        db.commit()
        message = "Successfully transferred $" + str(amount) + " to " + nickname[0][0] + " ."
    else:
        message = "Insufficient balance !!"
    return render_template('quickpay.html', message=message, beneficiaries=beneficiaries, accounts=accounts)


if __name__ == '__main__':
    app.run()
