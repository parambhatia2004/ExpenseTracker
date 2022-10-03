from crypt import methods
from curses import flash
from datetime import datetime
from email import message
from hashlib import new
from sre_constants import SUCCESS
from unicodedata import name
from urllib import request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from werkzeug import security
from flask_login import LoginManager, login_user, current_user, logout_user, login_required
# create the Flask app
from flask import Flask, render_template, request, session, redirect, jsonify, flash
from sqlalchemy import text
from markupsafe import escape



app = Flask(__name__)
app.secret_key = 'newsecret'
# select the database filename
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///todo.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# set up a 'model' for the data you want to store
from db_schema import db, User, Bill, BillPayees, dbinit

# init the database so it can connect with our app
db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)

# change this to False to avoid resetting the database every time this app is restarted
resetdb = True
if resetdb:
    with app.app_context():
        # drop everything, create all the tables, then put some data into the tables
        db.drop_all()
        db.create_all()
        dbinit()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
#route to the index
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/logout')
def logout():
    logout_user()
    return render_template('/index.html')


@app.route('/checkLogin', methods = ['POST'])
def checkLogin():
    username = request.form['username']
    password = request.form['password']
    
    user = User.query.filter_by(username=username).first()
    username=escape(username)
    if not user:
        return render_template('/login.html')

    if current_user.is_authenticated:
        return render_template('process.html')

    if security.check_password_hash(user.password, password):
        login_user(user)

        allBillsToPay = BillPayees.query.filter_by(users_id=current_user.id).all()
        for bills in allBillsToPay:
            if(bills.dateCreated > user.lastLogin):
                actualBill = Bill.query.filter_by(id=bills.bill_id).all()
                billPay = Bill.query.filter_by(id=bills.bill_id).all()
                print(billPay)
                for billsToPay in billPay:
                    userPayer = User.query.filter_by(id=billsToPay.user_id).all()
                    for users in userPayer:
                        flash('You have to pay $ ' + str(bills.cost) + ' to ' + str(users.username))

        user.lastLogin = datetime.now()
        db.session.commit()
        print(user.lastLogin)
        return render_template('/process.html')
    else:
        return render_template('/login.html')


@app.route('/register')
def reg():
    return render_template('/register.html')

@app.route('/newUser', methods = ['POST'])
def newUser():
    email = request.form['email']
    username = request.form['uname']
    password = request.form['password']
    repassword = request.form['repassword']

    if not username:
        return redirect('/register')
    if not password:
        return redirect('/register')

    if((User.query.filter_by(username=username).first()) is not None):
        flash("Username already taken")
        return redirect('/register')
    hashed_password = security.generate_password_hash(password)

    if security.check_password_hash(hashed_password, repassword):
        db.session.add(User(username, hashed_password, email, datetime.now()))
        db.session.commit()
        user = User.query.filter_by(username=username).first()
        login_user(user)
        return render_template('/process.html')

    else:
        return redirect('/register')

@app.route('/process')
def proc():
    if not current_user.is_authenticated:
        print("not logged in")
        return redirect('/')
    #test = BillPayees.query.filter_by(name="Ben").first().payee_status
    #print("hello")
    #print(test)
    
    return render_template('process.html')

@app.route('/removePayee', methods=['POST'])
def paid():
    if not current_user.is_authenticated:
        print("not logged in")
        return redirect('/')
    PayeeID = request.form['id']
    print("HE")
    print(PayeeID)
    firstpayee = BillPayees.query.filter_by(id=PayeeID).first()
    print("NOW")
    print(firstpayee)
    print("HERE")
    firstpayee.payer_status="true"
    db.session.commit()
    newPayee = BillPayees.query.filter_by(id=PayeeID).first()
    print(newPayee.payer_status)
    return jsonify(success=True)

@app.route('/falsePayment', methods=['POST'])
def falsePayment():
    if not current_user.is_authenticated:
        print("not logged in")
        return redirect('/')
    PayeeID = request.form['id']
    payee = BillPayees.query.filter_by(id=PayeeID).first()
    payee.payee_status = 'false'
    db.session.commit()
    return jsonify(success=True)


@app.route('/viewRaisedBills')
def view():
    if not current_user.is_authenticated:
        print("not logged in")
        return redirect('/')
    bills = Bill.query.filter_by(user_id=current_user.id).all()
    payingbills = BillPayees.query.filter_by(users_id=current_user.id).all()
    allOfBills = Bill.query.all()
    allUsers = User.query.all()
    payees = []
    billsToBePaid = []

    for allBills in bills:
        indivPayee = BillPayees.query.filter_by(bill_id=allBills.id)
        payees.extend(indivPayee)


    return render_template('view.html', bills=bills, payees=payees, payingbills=payingbills, allOfBills=allOfBills, allUsers=allUsers)

@app.route('/removeBillsRaised')
def removing():
    Bills = Bill.query.filter_by(user_id=current_user.id).all()
    payees =[]
    for bill in Bills:
        individualPayee = BillPayees.query.filter_by(bill_id=bill.id).all()
        payees.extend(individualPayee)
    return render_template('removeBills.html', Bills=Bills, payees=payees)

@app.route('/removingBill', methods=['POST'])
def deletion():
    BillID = request.form['id']
    print(BillID)

    billToRemove = Bill.query.filter_by(id=BillID).all()
    print(billToRemove)

    BillPayees.query.filter_by(bill_id=BillID).delete()
    

    Bill.query.filter_by(id=BillID).delete()
    db.session.commit()
    return jsonify(success=True)
@app.route('/addBill', methods=['POST'])
def addBill():
    if not current_user.is_authenticated:
        print("not logged in")
        return redirect('/')

    BillName = request.form['inputBillName']
    print(BillName)
    BillAmount = request.form['inputBillAmount']
    print(BillAmount)

    cost = int(BillAmount)
    ID = request.form.getlist('idArr[]')
    people = len(ID)
    print(len(ID))
    individualAmount = cost/people
    individualAmount = round(individualAmount, 2)
    print("THE COST IS " + str(individualAmount))
    db.session.add(Bill(BillName, BillAmount, current_user.id, people))
    print("added bill")
    print(BillName)
    print(people)
    db.session.commit()
    for user_id in ID:
        payee = User.query.filter_by(id=user_id).first().username
        print(payee)
        billID = Bill.query.filter_by(billName=BillName,amount=BillAmount, people=people).first().id
        print("bill id")
        print(billID)
        db.session.add(BillPayees(payee, user_id,individualAmount, "false","false", billID, datetime.now()))
        print("The time rn is " + str(datetime.now()))
    db.session.commit()
    return jsonify(success=True)
#    Amount = request.form['inputBillAmount']


@app.route('/userPaid', methods=['POST'])
def userPaid():
    if not current_user.is_authenticated:
        print("not logged in")
        return redirect('/')
    BillID = request.form['id']
    Payee = BillPayees.query.filter_by(id=BillID).first()
    print(Payee.payee_status)
    if(Payee.payee_status == "false"):
        Payee.payee_status = "true"
        db.session.commit()
        return jsonify(success=True)

    if(Payee.payee_status == "true"):
        Payee.payee_status = "false"
        db.session.commit()
        return jsonify({'error' : 'Missing data!'})

    newPayee = BillPayees.query.filter_by(bill_id=BillID).first().payee_status
    print(newPayee)

    return redirect('/view')

@app.route('/confirmPayments')
def confirmPayments():
    if not current_user.is_authenticated:
        print("not logged in")
        return redirect('/')
    allUserBillsRaised = Bill.query.filter_by(user_id=current_user.id).all()
    print(allUserBillsRaised)
    allUserBills = []
    billsPaid =[]
    for bills in allUserBillsRaised:
        print("hi")
        payeesPaid = BillPayees.query.filter_by(bill_id=bills.id, payee_status = "true", payer_status = "false").all()
        print(payeesPaid)
        billsPaid.extend(payeesPaid)
    print(billsPaid)
    return render_template('confirmPayments.html', billsPaid=billsPaid, allUserBillsRaised=allUserBillsRaised)

@app.route('/newItem', methods = ['POST'])
def newItem():
    newListItem = request.form['task']
    id = request.form['id']

    newListItem = escape(newListItem)
    id = escape(id)
    if not id:
        return render_template('/add.html')
    listId = int(id)
    qrytext = text("SELECT * FROM lists WHERE user_id=:id")
    qry = qrytext.bindparams(id=current_user.id)
    resultList = db.session.execute(qry)
    values = resultList.fetchall()

#    current_user_list = List.query.filter_by(user_id=current_user.id)
    if listId > len(values):
        return render_template('/add.html')

    desiredList = values[listId - 1];

    querytext = text("SELECT id FROM lists WHERE name=:listname")
    query = querytext.bindparams(listname = desiredList.name)
    result = db.session.execute(query)
    item = result.fetchall()
    final = []
    for id in item:
        final.extend(id)
    #item = List.query.filter_by(name = desiredList.name).first().id

    insertion = text("INSERT INTO task (task, completed, list_id) VALUES (:newListItem, :status, :list_id);")
    insert = insertion.bindparams(newListItem=newListItem, status="false", list_id=final[0])
    db.session.execute(insert)
    #db.session.add(ListItem(newListItem, "false", item))
    db.session.commit()
    return render_template('process.html')
