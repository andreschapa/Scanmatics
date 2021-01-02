#views

from functools import wraps
from flask import Flask, flash, redirect, render_template, \
request, session, url_for
from flask_sqlalchemy import SQLAlchemy
from forms import AddCustomerForm
#config

app=Flask(__name__)
app.config.from_object('_config')
db=SQLAlchemy(app)

from models import Customer

#helper functions

def login_required(test):
    @wraps(test)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return test(*args, **kwargs)
        else:
            flash('You need to login first.')
            return redirect(url_for('login'))
    return wrap

#route handlers

@app.route('/logout/')
def logout():
    session.pop('logged_in', None)
    flash('Adios!')
    return redirect(url_for('login'))

@app.route('/', methods=['GET', 'POST'])
def login():
    error=None
    if request.method== 'POST':
        if request.form['username'] != app.config['USERNAME'] \
            or request.form['password'] != app.config['PASSWORD']:
            error='Invalid Credentials. Please try again.'
            return render_template('login.html', error=error)
        else:
            session['logged_in']= True
            flash('Welcome!')
            return redirect(url_for('main'))
    return render_template('login.html')


@app.route('/main/')
@login_required
def main():
    customers=db.session.query(Customer).order_by(Customer.name.asc())  ##Wil need to change structure of how to query based on which customer from certain company is logged in. 
    return render_template(
        'main.html',
        form=AddCustomerForm(request.form),
        customers=customers)

#add new customer
@app.route('/addcustomer/', methods=['POST'])
@login_required
def new_customer():
    form=AddCustomerForm(request.form)
    if request.method=='POST':
        if form.validate_on_submit():
            new_customer=Customer(
                form.name.data
            )
            db.session.add(new_customer)
            db.session.commit()
            flash('New customer was successfully added. Thanks.')
    return redirect (url_for('main'))
    
#delete customer
@app.route('/delete/<int:customer_id>/') ##<name> is the column 'name' in the customers data base where customers are listed
@login_required
def delete_customer(customer_id):
    new_id = customer_id
    db.session.query(Customer).filter_by(customer_id=new_id).delete()
    db.session.commit()
    flash('Customer has been deleted.')
    return redirect(url_for('main'))
