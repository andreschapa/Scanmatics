#views

import sqlite3
from functools import wraps

from flask import Flask, flash, redirect, render_template, request, session, url_for, g
from forms import AddCustomerForm
#config

app=Flask(__name__)
app.config.from_object('_config')

#helper functions

def connect_db():
    return sqlite3.connect(app.config['DATABASE_PATH'])

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
    g.db=connect_db()
    cursor=g.db.execute('select customer_id, name from customers')

    customers=[
        dict(customer_id=row[0], name=row[1]) for row in cursor.fetchall()]
    g.db.close()
    return render_template(
        'main.html',
        form=AddCustomerForm(request.form),
        customers=customers)

#add new customer
@app.route('/addcustomer/', methods=['POST'])
@login_required
def new_customer():
    g.db=connect_db()
    name=request.form['name']
    if not name:
        flash("Please enter name of new customer you would like to create.")
        return redirect(url_for('main'))
    else:
        g.db.execute('insert into customers (name) values (?)',[request.form['name']]) #table name will need to be dynamic in the future for multiple customers of scanmatics
        g.db.commit()
        g.db.close()
        flash('New customer was successfully added. Thanks.')
        return redirect (url_for('main'))
    
#delete customer
@app.route('/delete/<int:customer_id>/') ##<name> is the column 'name' in the customers data base where customers are listed
@login_required
def delete_customer(customer_id):
    g.db=connect_db()
    g.db.execute('delete from customers where customer_id='+str(customer_id))
    g.db.commit()
    g.db.close()
    flash('Customer has been deleted.')
    return redirect(url_for('main'))
