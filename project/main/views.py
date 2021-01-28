#views
from .forms import AddCustomerForm, RegisterForm, LoginForm, AddProjectForm, AddPanelForm,RegisterQRForm

from functools import wraps
from flask import Flask, flash, redirect, render_template, \
request, session, url_for, Response, Blueprint
from sqlalchemy.exc import IntegrityError

from project.models import Customer, User, Project, Panel, QRcode
from project import db, bcrypt
main_blueprint= Blueprint('main', __name__)

import boto3
import os

S3_BUCKET=os.environ.get('S3_BUCKET')
s3=boto3.client('s3')

#S# for configuring locally
#from .s3config import S3_BUCKET, S3_KEY, S3_SECRET
#s3=boto3.client(
    #'s3',
    #aws_access_key_id=S3_KEY,
   # aws_secret_access_key=S3_SECRET
#)



############# QR CODE SHIT WILL MOVE THIS TO THE BOTTOM ONCE DONE WITH DEVELOPMENT##################
#register QR code
@main_blueprint.route('/QRmain/<int:QR_id>', methods=['GET', 'POST'])
def QRmain(QR_id):
    QR_id=QR_id
    error=None
    form=RegisterQRForm(request.form)
    
    #checks if qr ID exists in the QR code table. If exists then it takes you to its data.
    qrcode=QRcode.query.filter_by(QR_id=QR_id).first()
    if qrcode is not None :
        panel_id=qrcode.panel_id #pulling panel ID from QRcode model
        return redirect(url_for('main.QRfiles',panel_id=panel_id))

    if request.method== 'POST':
        if form.validate_on_submit():
            PID=request.form['panel_id']
            panel=Panel.query.filter_by(panel_id=PID).first()
            PanelID=panel.panel_id
            ##checks if panel exists
            
            if panel is not None and PanelID == PID: #and panel.project_id == request.form['project_id'] and panel.panel_name == request.form['panel_name']:
               

                new_QR= QRcode(
                form.panel_id.data,
                form.project_id.data,
                form.panel_name.data,
                QR_id
                )
                try:
                    db.session.add(new_QR)
                    db.session.commit()
                    flash('Thanks for registering QR code.')
                    return redirect(url_for('main.login')) #### change this to the QR URL
                except IntegrityError: #Verify integrity error works for other shit besides email
                    error= 'That panel ID has already been linked to a QR code.'
                    return render_template('QR_register.html', form=form, error=error)

            else:
                error= 'Panel ID, Project ID and Panel Name must be exact match. Panel name is case sensitive. '
                return render_template('QR_register.html', form=form, error=error)

            if panel is None:

                error= 'That panel does not exist'
                return render_template('QR_register.html', form=form, error=error)
            ##checks that panel id, project ID, and panel name is exact for data protection purposes
            panel=Panel.query.filter_by(panel_id=PID).first()
    return render_template('QR_register.html', form=form, error=error)



###
@main_blueprint.route('/QRfiles/<int:panel_id>/')
def QRfiles(panel_id):
    qrcode=QRcode.query.filter_by(panel_id=panel_id).first()
    if qrcode is None:
        return redirect(url_for('main.login'))

    #Panels=db.session.query(Panel).filter_by(panel_id=panel_id).order_by(Panel.name.asc())
    panels=Panel.query.filter_by(panel_id=panel_id).first()
    project_id=panels.panel_project_id
    panel_id=panels.panel_id
    PANEL_ID=str(panel_id)
    panel_name=panels.name

    s3_resource=boto3.resource('s3')
    my_bucket=s3_resource.Bucket(S3_BUCKET)
    #summaries=my_bucket.objects.all()
    summaries=my_bucket.objects.filter(Prefix=f'{PANEL_ID}/')
    
    return render_template('QR_dataview.html', my_bucket=my_bucket, files=summaries, project_id=project_id, panel_id=panel_id, panel_name=panel_name )
 ####   






    
#register customer
@main_blueprint.route('/register/', methods=['GET', 'POST'])
def register():
    error=None
    form=RegisterForm(request.form)
    if request.method== 'POST':
        if form.validate_on_submit():
            new_user= User(
                form.name.data,
                form.email.data,
                bcrypt.generate_password_hash(form.password.data).decode('utf-8'),####### added.decode(utf-8)
                form.company.data,
            )
            try:
                db.session.add(new_user)
                db.session.commit()
                flash('Thanks for registering. Please login.')
                return redirect(url_for('main.login'))
            except IntegrityError:
                error= 'That username and/or email already exists.'
                return render_template('register.html', form=form, error=error)
    return render_template('register.html', form=form, error=error)






def login_required(test):
    @wraps(test)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return test(*args, **kwargs)
        else:
            flash('You need to login first.')
            return redirect(url_for('main.login'))
    return wrap

#route handlers

@main_blueprint.route('/logout/')
def logout():
    session.pop('logged_in', None)
    session.pop('company_id', None)
    session.pop('name', None)
    flash('Adios!')
    return redirect(url_for('main.login'))

@main_blueprint.route('/', methods=['GET', 'POST'])
def login():
    error=None
    form= LoginForm(request.form)
    if request.method== 'POST':
        if form.validate_on_submit():
            user=User.query.filter_by(name=request.form['name']).first()
            if user is not None and bcrypt.check_password_hash(user.password, request.form['password']) and user.company == request.form['company']:
                session['logged_in']= True
                session['company_id']=user.company
                session['name']=user.name
                flash('Welcome!')
                return redirect(url_for('main.main'))
            else:
                error= 'Invalid username, company name, or password.'
        else:
            error= 'All fields are required.'
    return render_template('login.html', form=form, error=error)
       

@main_blueprint.route('/main/')
@login_required
def main():
    customers=db.session.query(Customer).filter_by(company_id = session['company_id']).order_by(Customer.name.asc())
    return render_template(
        'main.html',
        form=AddCustomerForm(request.form),
        customers=customers,
        username=session['name']
        )

#add new customer
@main_blueprint.route('/addcustomer/', methods=['POST'])
@login_required
def new_customer():
    form=AddCustomerForm(request.form)
    if request.method=='POST':
        if form.validate_on_submit():
            new_customer=Customer(
                form.name.data,
                session['company_id']
            )
            db.session.add(new_customer)
            db.session.commit()
            flash('New customer was successfully added. Thanks.')
        else :
            flash('ERROR Please enter customer name')
    return redirect (url_for('main.main'))
    
#delete customer. Deletes all projects and panels associated with this customer
@main_blueprint.route('/delete/<int:customer_id>/') ##<name> is the column 'name' in the customers data base where customers are listed
@login_required
def delete_customer(customer_id):
    new_id = customer_id
    db.session.query(Customer).filter_by(customer_id=new_id).delete()
    db.session.query(Project).filter_by(project_customer_id=new_id).delete()
    db.session.query(Panel).filter_by(panel_project_customer_id=new_id).delete()
    db.session.commit()
    flash('Customer and data has been deleted.')
    return redirect(url_for('main.main'))


@main_blueprint.route('/projects/<int:customer_id>') ##return <int: customer_id>
@login_required
def projects(customer_id):
    
    projects=db.session.query(Project).filter_by(project_customer_id = customer_id).order_by(Project.name.asc())
    project_customer_id=customer_id
    customer=Customer.query.filter_by(customer_id=customer_id).first()
    customer_name=customer.name
    return render_template(
        'projects.html',
        form=AddProjectForm(request.form),
        projects=projects,
        project_customer_id=customer_id,
        customer_name=customer_name)

@main_blueprint.route('/deleteproject/<int:project_id>/') ##<name> is the column 'name' in the customers data base where customers are listed
@login_required
def delete_project(project_id):
    new_id = project_id
    project=Project.query.filter_by(project_id=project_id).first()
    customer_id=project.project_customer_id
    db.session.query(Project).filter_by(project_id=new_id).delete()
    db.session.query(Panel).filter_by(panel_project_id=new_id).delete()
    db.session.commit()
    flash('project has been deleted.')
    return redirect(url_for('main.projects', customer_id=customer_id))
    


@main_blueprint.route('/addproject/<int:project_customer_id>', methods=[ 'GET', 'POST'])
@login_required
def new_project(project_customer_id):
    form=AddProjectForm(request.form)
    if request.method=='POST':
        if form.validate_on_submit():
            
            new_project=Project(
                form.name.data,
                project_customer_id
            )
               
            db.session.add(new_project)
            db.session.commit()
            flash('New project was successfully added. Thanks.')
    return redirect (url_for('main.projects',customer_id=project_customer_id))

@main_blueprint.route('/panels/<int:project_id>')
@login_required
def panels(project_id):
    panels=db.session.query(Panel).filter_by(panel_project_id=project_id).order_by(Panel.name.asc())
    projects=Project.query.filter_by(project_id=project_id).first()
    panel_project_id=project_id
    panel_project_customer_id=projects.project_customer_id 
    #code to grab specific panel name to pass to panels.html
    project_name=projects.name#code to grab specific panel name to pass to panels.html

    return render_template(
        'panels.html',
        form=AddPanelForm(request.form),
        panels=panels,
        panel_project_id=project_id,
        panel_project_customer_id=panel_project_customer_id,
        project_name=project_name
    )

@main_blueprint.route('/addpanel/<int:panel_project_id>', methods=[ 'GET', 'POST'])
@login_required
def new_panel(panel_project_id):
    form=AddProjectForm(request.form)
    project=Project.query.filter_by(project_id=panel_project_id).first()
    panel_project_customer_id=project.project_customer_id
    if request.method=='POST':
        if form.validate_on_submit():
            
            new_panel=Panel(
                form.name.data,
                panel_project_id,  
                panel_project_customer_id

            )
               
            db.session.add(new_panel)
            db.session.commit()
            flash('New panel was successfully added to project. Thanks.')
    return redirect (url_for('main.panels',project_id=panel_project_id))

@main_blueprint.route('/deletepanel/<int:panel_id>/') ##<name> is the column 'name' in the customers data base where customers are listed
@login_required
def delete_panel(panel_id):
    new_id = panel_id
    panel=Panel.query.filter_by(panel_id=panel_id).first()
    project_id=panel.panel_project_id
    db.session.query(Panel).filter_by(panel_id=new_id).delete()
    db.session.commit()
    flash('Panel has been deleted.')
    return redirect(url_for('main.panels', project_id=project_id))
    

##########################
@main_blueprint.route('/files/<int:panel_id>/')
@login_required
def files(panel_id):
    #Panels=db.session.query(Panel).filter_by(panel_id=panel_id).order_by(Panel.name.asc())
    panels=Panel.query.filter_by(panel_id=panel_id).first()
    project_id=panels.panel_project_id
    panel_id=panels.panel_id
    PANEL_ID=str(panel_id)
    panel_name=panels.name

    s3_resource=boto3.resource('s3')
    my_bucket=s3_resource.Bucket(S3_BUCKET)
    #summaries=my_bucket.objects.all()
    summaries=my_bucket.objects.filter(Prefix=f'{PANEL_ID}/')
    
    return render_template('files.html', my_bucket=my_bucket, files=summaries, project_id=project_id, panel_id=panel_id, panel_name=panel_name )

@main_blueprint.route('/upload/<int:panel_id>/', methods=['POST'])
def upload(panel_id):
    file=request.files['file']
    panels=Panel.query.filter_by(panel_id=panel_id).first()
    panel_id=panels.panel_id
    
    PANEL_ID=str(panel_id) #added this
    
    key= f"{PANEL_ID}/"+file.filename


    s3_resource=boto3.resource('s3')
    my_bucket=s3_resource.Bucket(S3_BUCKET)
    #my_bucket.Object(file.filename).put(Body=file,Tagging=f'panel_id={PANEL_ID}') ##changed this. added tagging
    
    my_bucket.Object(file.filename).put(Body=file, Key=key)

    flash('File uploaded successfully')

    return redirect(url_for('main.files', panel_id=panel_id))

@main_blueprint.route('/delete/<int:panel_id>', methods=['POST'])
def delete(panel_id):
    key=request.form['key']

    panels=Panel.query.filter_by(panel_id=panel_id).first()
    panel_id=panels.panel_id

    s3_resource=boto3.resource('s3')
    my_bucket=s3_resource.Bucket(S3_BUCKET)
    my_bucket.Object(key).delete()

    flash('File deleted successfully')
    return redirect(url_for('main.files', panel_id=panel_id))

@main_blueprint.route('/download/<int:panel_id>', methods=['POST'])
def download(panel_id):
    panels=Panel.query.filter_by(panel_id=panel_id).first()
    panel_id=panels.panel_id

    key=request.form['key']
    s3_resource=boto3.resource('s3')
    my_bucket=s3_resource.Bucket(S3_BUCKET)

    file_obj=my_bucket.Object(key).get()

    return Response(
        file_obj['Body'].read(),
        mimetype='text/plain',
        headers={"Content-Disposition": "attachment;filename={}".format(key)}

    )


