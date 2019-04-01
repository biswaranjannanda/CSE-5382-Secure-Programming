import now as now
from flask import Flask, render_template, request, session
import mysql.connector
import hashlib
import datetime
import os
import re
from validate_email import validate_email
import logging

DB = mysql.connector.connect(user='root', password='root', host='127.0.0.1', database='thomaspay')
#DB = mysql.connector.connect(user='root', password='root-123', host='thomaspay.clp7fwlohsdk.us-east-2.rds.amazonaws.com', database='thomaspay')

print ('---' + str(DB))
CURSOR = DB.CURSOR()  # create a new CURSOR for establishing the query

app = Flask(__name__)
app.secret_key = os.urandom(24)


@app.route('/')
def hello_world():
    return render_template('index.html')

@app.route('/login', methods=['POST', 'GET'])
def login():
    try:
        username = request.form['username']
        password = request.form['password']
        if re.search(r"""^^[A-Za-z0-9@#$%^&+=]{8,}$""", password):
            print("Valid Password!")
        else:
            message = "Incorrect details entered"
            return render_template('index.html', message=message)
        dk = hashlib.pbkdf2_hmac('SHA256', password, b'salt', 100000).encode('base64').strip()
        print(len(dk))
        if re.search(r"""^^[a-zA-Z0-9]+([a-zA-Z0-9](_|-| )[a-zA-Z0-9])*[a-zA-Z0-9]+$""", username):
            print("Valid username!")
        else:
            message = "Incorrect details entered"
            return render_template('index.html', message=message)

        query = "select count(*) from thomaspay.users where username = '" + str(username) + "' and password = '" + dk + "'"
        print (query)
        CURSOR.execute(query)
        data = CURSOR.fetchall()
        print(data)
        if data[0][0] != 0:
            session['user'] = username
            user = session['user']
            # print (session['user']
            query1 = "select balance from thomaspay.wallet,thomaspay.users " \
                     "where thomaspay.users.username='" + session['user'] + "' and thomaspay.users.user_id = thomaspay.wallet.user_id"
            print(query1)
            CURSOR.execute(query1)
            data1 = CURSOR.fetchall()
            print(data1)
            return render_template('homepage.html', data1=data1, user=user)
        else:
            message = "Incorrect username or Password"
            return render_template('index.html', message=message)
    except Exception as e:
        logging.basicConfig(filename='tpay.log', filemode='a', format='%(name)s - %(levelname)s - %(message)s')
        logging.error("---------------------------------------------------------------------------------------")
        logging.error("USER DETAIL: %s", session['user'])
        logging.error(":THOMAS PAY ERROR DETAIL:", exc_info=True)
        result = "Some internal error has occured. if problem continues please contact our help desk associate"
        return render_template('/index.html', result=result)



@app.route('/addbeneficiaryhome', methods = ['POST','GET'])
def addbeneficiaryhome():
    return render_template('addbeneficiary.html')

@app.route('/addbeneficiary', methods = ['POST','GET'])
def addbeneficiary():
    if request.method == 'POST':
        nickname = request.form['nickname']
        email = request.form['email']

        nick_pattern = re.compile(r"[a-zA-Z0-9]+")

        # input validation
        if not validate_email(email):
            result = "Enter Valid email"
            return render_template('/addbeneficiary.html', result=result)

        if not nick_pattern.match(nickname):
            result = "only alpha numeric characters are allowed"
            return render_template('/addbeneficiary.html', result=result)

        # getting the user_id of beneficiary
        query1 = "SELECT user_id from thomaspay.users WHERE user_emailid = '" + str(email) + "'"
        print(query1)

        try:

            query1 = "SELECT user_id from thomaspay.users WHERE user_emailid = '" + str(email) + "'"
            print(query1)
            CURSOR.execute(query1)
            bef_userid = CURSOR.fetchall()
            print(bef_userid)

            # Getting the user id of current logged in user
            query2 = "Select user_id from thomaspay.users WHERE username =  '" + session['user'] + "' "
            print(query2)
            CURSOR.execute(query2)
            userid = CURSOR.fetchall()
            user_mod = userid[0][0]
            # print(user_mod)

            # If beneficiary is not found
            if not bef_userid:
                result = "User Does not exist"
                return render_template('/addbeneficiary.html', result=result)
            # If user tries to add himself
            elif user_mod == bef_userid[0][0]:
                result = "You cannot add yourself as beneficiary"
                return render_template('/addbeneficiary.html', result=result)
            else:
                query = "INSERT into thomaspay.beneficiary ( user_id, beneficiary_id, nickname, email_id)" \
                        "VALUES (%s,%s,%s,%s)"
                val1 = (user_mod, int(bef_userid[0][0]), nickname, email)

                CURSOR.execute(query, val1)

                DB.commit()

                # print(query)

                result = "Beneficiary added Successfuly."
                return render_template('/addbeneficiary.html', result=result)
        except Exception as e:

            logging.basicConfig(filename='tpay.log', filemode='a', format='%(name)s - %(levelname)s - %(message)s')
            logging.error("---------------------------------------------------------------------------------------")
            logging.error("USER DETAIL: %s", session['user'])
            logging.error(":THOMAS PAY ERROR DETAIL:", exc_info=True)
            result = "Some internal error has occured. if problem continues please contact our help desk associate"
            return render_template('/addbeneficiary.html', result=result)


@app.route('/addmoney', methods=['POST', 'GET'])
def addmoney():
    try:
        query = "SELECT card_name,cardnumber FROM thomaspay.account,thomaspay.users " \
                "where thomaspay.users.username='" + session['user'] + "' and thomaspay.users.user_id = thomaspay.account.user_id"
        print(query)
        CURSOR.execute(query)
        data = CURSOR.fetchall()
        print(data)
        return render_template('addmoney.html', data=data)
    except Exception as e:

        logging.basicConfig(filename='tpay.log', filemode='a', format='%(name)s - %(levelname)s - %(message)s')
        logging.error("---------------------------------------------------------------------------------------")
        logging.error("USER DETAIL: %s", session['user'])
        logging.error(":THOMAS PAY ERROR DETAIL:", exc_info=True)
        result = "Some internal error has occured. if problem continues please contact our help desk associate"
        return render_template('/addmoney.html', result=result)



@app.route('/addmoneytodb', methods=['POST', 'GET'])
def addmoneytodb():
    try:
        money = request.form['money']
        money1 = float(money)
        if re.search(r"""^^(?!-).*[0-9]+(\.[0-9]{1,2})?$""", money):
            print("Valid Amounnt!")
        else:
            message = "Invalid amount entered!!"
            return render_template('addmoney.html', message=message)

        query = "SELECT card_name,cardnumber FROM thomaspay.account,thomaspay.users " \
                "where thomaspay.users.username='" + session['user'] + "' and thomaspay.users.user_id = thomaspay.account.user_id"
        print(query)
        CURSOR.execute(query)
        data = CURSOR.fetchall()
        if money1 < 0:
            message1 = "Enter a valid amount"
            return render_template('addmoney.html', data=data, message1=message1)
        else:
            print(money1)
            now = datetime.datetime.now()
            date = now.strftime("%Y-%m-%d")
            query0 = "select thomaspay.users.user_id, thomaspay.wallet.balance from thomaspay.wallet, thomaspay.users where thomaspay.users.user_id = thomaspay.wallet.user_id " \
                     "and thomaspay.users.username='" + session['user'] + "'"
            CURSOR.execute(query0)
            datas = CURSOR.fetchall()
            uid = datas[0][0]
            balance = datas[0][1]
            print(query0)
            print(balance)
            currentbalance = float(balance)
            updatedbalance = money1 + currentbalance
            print("updated Balance = " + str(updatedbalance))
            query2 = "UPDATE thomaspay.wallet SET balance = %s WHERE user_id = %s"
            val3 = (int(updatedbalance), int(uid))
            CURSOR.execute(query2, val3)

            query1 = "insert into thomaspay.transactions(user_id, transaction_type, amount, transaction_date, sendto, receivedfrom) " \
                     "values(%s, %s, %s, %s, %s, %s)"
            val1 = (int(uid), 'Credit', float(money1), date, 'null', 'Wallet Updated')
            CURSOR.execute(query1, val1)

            DB.commit()
            print('money updated in db')
            message = "Money successfully added to your wallet !!"

        return render_template('addmoney.html', data=data, message=message)
    except Exception as e:

        logging.basicConfig(filename='tpay.log', filemode='a', format='%(name)s - %(levelname)s - %(message)s')
        logging.error("---------------------------------------------------------------------------------------")
        logging.error("USER DETAIL: %s", session['user'])
        logging.error(":THOMAS PAY ERROR DETAIL:", exc_info=True)
        result = "Some internal error has occured. if problem continues please contact our help desk associate"
        return render_template('/addmoney.html', result=result)



@app.route('/homepage', methods=['POST', 'GET'])
def homepage():
    try:
        query1 = "select balance from thomaspay.wallet,thomaspay.users " \
                 "where thomaspay.users.username='" + session['user'] + "' and thomaspay.users.user_id = thomaspay.wallet.user_id"
        print(query1)
        CURSOR.execute(query1)
        data1 = CURSOR.fetchall()
        print(data1)
        return render_template('homepage.html', data1=data1)
    except Exception as e:

        logging.basicConfig(filename='tpay.log', filemode='a', format='%(name)s - %(levelname)s - %(message)s')
        logging.error("---------------------------------------------------------------------------------------")
        logging.error("USER DETAIL: %s", session['user'])
        logging.error(":THOMAS PAY ERROR DETAIL:", exc_info=True)
        result = "Some internal error has occured. if problem continues please contact our help desk associate"
        return render_template('/homepage.html', result=result)



@app.route('/logout')
def logout():
    session.pop('user', None)
    return render_template('index.html')



@app.route('/viewtransaction', methods=['POST', 'GET'])
def viewtransaction():
    return render_template('viewtransactions.html')


@app.route('/transactions', methods=['POST', 'GET'])
def transations():
    try:
        results = []
        periodfrom = request.form['periodfrom']
        periodto = request.form['periodto']
        if re.search(r"""^^([12]\d{3}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01]))$""", periodfrom):
            print("Valid Date!")
        else:
            message = "InValid Date entered!!"
            return render_template('viewtransactions.html', message=message)
        if re.search(r"""^^([12]\d{3}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01]))$""", periodto):
            print("Valid Date!")
        else:
            message = "InValid Date entered!!"
            return render_template('viewtransactions.html', message=message)
        query = "SELECT transaction_id,transaction_date,transaction_type,sendto,receivedfrom,amount FROM thomaspay.transactions,thomaspay.users " \
                "where users.username='" + session['user'] + "' and thomaspay.users.user_id = thomaspay.transactions.user_id and transaction_date between '" + str(
            periodfrom) + "' and '" + str(periodto) + "'"
        CURSOR.execute(query)
        data = CURSOR.fetchall()
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
    except Exception as e:

        logging.basicConfig(filename='tpay.log', filemode='a', format='%(name)s - %(levelname)s - %(message)s')
        logging.error("---------------------------------------------------------------------------------------")
        logging.error("USER DETAIL: %s", session['user'])
        logging.error(":THOMAS PAY ERROR DETAIL:", exc_info=True)
        result = "Some internal error has occured. if problem continues please contact our help desk associate"
        return render_template('/viewtransactions.html', result=result)



# link account
@app.route('/linkaccount', methods=['POST', 'GET'])
def linkaccount():
    try:
        return render_template('linkaccount.html')
    except Exception as e:

        logging.basicConfig(filename='tpay.log', filemode='a', format='%(name)s - %(levelname)s - %(message)s')
        logging.error("---------------------------------------------------------------------------------------")
        logging.error("USER DETAIL: %s", session['user'])
        logging.error(":THOMAS PAY ERROR DETAIL:", exc_info=True)
        result = "Some internal error has occured. if problem continues please contact our help desk associate"
        return render_template('/linkaccount.html', result=result)



@app.route('/linkacc', methods=['POST', 'GET'])
def linkacc():
    try:
        card_type = str(request.form['card_type'])
        card_number = str(request.form['card_number'])
        if re.search(r"""^[0-9]{16}?$""", card_number):
            print("Valid card_number!")
        else:
            message = "Card Number Invalid!"
            return render_template('linkaccount.html', message=message)
        cvv_number = str(request.form['cvv_number'])
        if re.search(r"""^[0-9]{3,4}?$""", cvv_number):
            print("Valid cvv_number!")
        else:
            message = "CVV Invalid!"
            return render_template('linkaccount.html', message=message)
        month_year = str(request.form['month'])
        x = month_year.split("-")
        now = datetime.datetime.now()
        date = now.strftime("%Y-%m")
        current=date.split("-")
        if x[0] > current[0] or (x[0] == current[0] and (x[1] >= current[1])):
            query1 = "select user_id from thomaspay.users where username='" + session[
                                     'user']+"'"
            print(query1)
            CURSOR.execute(query1)
            uid = CURSOR.fetchall()
            print(uid[0][0])
            print(type(card_number), type(card_type), type(cvv_number), type(x[0]), type(x[1]), type(uid[0][0]))

            query = "insert into thomaspay.account(user_id, card_name, cardnumber, cvv, month, year) values(%s, %s, %s, %s, %s, %s)"
            val = (int(uid[0][0]), card_type, card_number, cvv_number, x[1], x[0])
            print (query)
            CURSOR.execute(query, val)
            DB.commit()
            message = "Card  Details Entered !!!!!!!!!!!!!!!!!!!!"
        else:
            message = "Card Expired !!!!!!!!!!!!!!!!"
        return render_template('linkaccount.html', message=message)
    except Exception as e:

        logging.basicConfig(filename='tpay.log', filemode='a', format='%(name)s - %(levelname)s - %(message)s')
        logging.error("---------------------------------------------------------------------------------------")
        logging.error("USER DETAIL: %s", session['user'])
        logging.error(":THOMAS PAY ERROR DETAIL:", exc_info=True)
        result = "Some internal error has occured. if problem continues please contact our help desk associate"
        return render_template('/linkaccount.html', result=result)



# quickpay
@app.route('/quickpay', methods=['POST', 'GET'])
def quickpay():
    try:
        beneficiaries = getBeneficiaries()
        accounts = getAccounts()
        return render_template('quickpay.html', beneficiaries=beneficiaries, accounts=accounts)
    except Exception as e:

        logging.basicConfig(filename='tpay.log', filemode='a', format='%(name)s - %(levelname)s - %(message)s')
        logging.error("---------------------------------------------------------------------------------------")
        logging.error("USER DETAIL: %s", session['user'])
        logging.error(":THOMAS PAY ERROR DETAIL:", exc_info=True)
        result = "Some internal error has occured. if problem continues please contact our help desk associate"
        return render_template('/quickpay.html', result=result)




@app.route('/getBeneficiaries', methods=['POST', 'GET'])
def getBeneficiaries():
    try:
        query1 = "select beneficiary_id, nickname from thomaspay.beneficiary, thomaspay.users " \
                 "where thomaspay.beneficiary.user_id=thomaspay.users.user_id and thomaspay.users.username = '" + session['user'] + "'"
        print(query1)
        CURSOR.execute(query1)
        results = CURSOR.fetchall()
        print(results)
        return results
    except Exception as e:

        logging.basicConfig(filename='tpay.log', filemode='a', format='%(name)s - %(levelname)s - %(message)s')
        logging.error("---------------------------------------------------------------------------------------")
        logging.error("USER DETAIL: %s", session['user'])
        logging.error(":THOMAS PAY ERROR DETAIL:", exc_info=True)
        result = "Some internal error has occured. if problem continues please contact our help desk associate"
        return None


@app.route('/getAccounts', methods=['POST', 'GET'])
def getAccounts():
    try:
        query1 = "select account_id, cardnumber, card_name from thomaspay.account, thomaspay.users " \
                 "where thomaspay.account.user_id=thomaspay.users.user_id and thomaspay.users.username = '" + session['user'] + "'"
        print(query1)
        CURSOR.execute(query1)
        results = CURSOR.fetchall()
        print(results)
        return results
    except Exception as e:

        logging.basicConfig(filename='tpay.log', filemode='a', format='%(name)s - %(levelname)s - %(message)s')
        logging.error("---------------------------------------------------------------------------------------")
        logging.error("USER DETAIL: %s", session['user'])
        logging.error(":THOMAS PAY ERROR DETAIL:", exc_info=True)
        result = "Some internal error has occured. if problem continues please contact our help desk associate"
        return None



@app.route('/quickpayamount', methods=['POST', 'GET'])
def quickpayamount():
    try:
        beneficiaries = getBeneficiaries()
        accounts = getAccounts()
        now = datetime.datetime.now()
        date = now.strftime("%Y-%m-%d")
        beneficiary = str(request.form['beneficiary'])
        amount = request.form['amount']
        if re.search(r"""^^(?!-).*[0-9]+(\.[0-9]{1,2})?$""", amount):
            print("Valid amount entered!")
        else:
            message = "Invalid ammount entered..!"
            return render_template('quickpay.html', message=message, beneficiaries=beneficiaries, accounts=accounts)
        query0 = "select thomaspay.users.user_id, thomaspay.wallet.balance from thomaspay.wallet, thomaspay.users where thomaspay.users.user_id = thomaspay.wallet.user_id " \
                 "and thomaspay.users.username='" + session['user'] + "'"
        CURSOR.execute(query0)
        data = CURSOR.fetchall()
        uid = data[0][0]
        balance = data[0][1]
        print(uid)
        amount = int(amount)
        print(amount)
        print(date, beneficiary, amount)
        if balance >= amount:
            query11 = "select nickname from thomaspay.beneficiary where beneficiary_id = %s and user_id = %s"
            val11 = (int(beneficiary), int(uid))
            CURSOR.execute(query11, val11)
            nickname = CURSOR.fetchall()
            print(nickname[0][0])
            query1 = "insert into thomaspay.transactions(user_id, transaction_type, amount, transaction_date, sendto, receivedfrom) " \
                    "values(%s, %s, %s, %s, %s, %s)"
            val1 = (int(uid), 'Debit', float(amount), date, nickname[0][0], 'null')
            val2 = (beneficiary, 'Credit', float(amount), date, 'null', session['user'])
            CURSOR.execute(query1, val1)
            CURSOR.execute(query1, val2)
            query2 = "UPDATE thomaspay.wallet SET balance = balance - %s WHERE user_id = %s and balance >= %s"
            val3 = (float(amount), int(uid), float(amount))
            CURSOR.execute(query2, val3)
            query3 = "UPDATE thomaspay.wallet SET balance = balance + %s WHERE user_id = %s and balance >= %s"
            val4 = (float(amount), int(beneficiary), float(amount))
            CURSOR.execute(query3, val4)
            DB.commit()
            message = "Successfully transferred $"+str(amount)+" to "+nickname[0][0]+" ."
        else:
            message = "Insufficient balance..."
        return render_template('quickpay.html', message=message, beneficiaries=beneficiaries, accounts=accounts)
    except Exception as e:

        logging.basicConfig(filename='tpay.log', filemode='a', format='%(name)s - %(levelname)s - %(message)s')
        logging.error("---------------------------------------------------------------------------------------")
        logging.error("USER DETAIL: %s", session['user'])
        logging.error(":THOMAS PAY ERROR DETAIL:", exc_info=True)
        result = "Some internal error has occured. if problem continues please contact our help desk associate"
        return render_template('/quickpay.html', result=result)


if __name__ == '__main__':
    app.run()