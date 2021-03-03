#views
from .forms import AddCustomerForm, RegisterForm, LoginForm, AddProjectForm, AddPanelForm,RegisterQRForm, RequestResetForm, ResetPasswordForm, SendEmailLink, AddMaintenanceLog

from functools import wraps
from flask import Flask, flash, redirect, render_template, \
request, session, url_for, Response, Blueprint
from sqlalchemy.exc import IntegrityError
from flask_mail import Message, Mail
from project.models import Customer, User, Project, Panel, QRcode, Maintenance_Logs
from project import db, bcrypt , mail
main_blueprint= Blueprint('main', __name__)

import boto3
import os
import datetime

S3_BUCKET=os.environ.get('S3_BUCKET')
s3=boto3.client('s3')

def login_required(test):
    @wraps(test)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return test(*args, **kwargs)
        else:
            flash('You need to login first.')
            return redirect(url_for('main.login'))
    return wrap

########################### Maintenance Logs ##############################################
#def open_logs():
   #return db.session.query(Maintenance_Logs).filter_by(MaintenanceLog_panel_id=panel_id, status= '1').order_by(Maintenance_Logs.priority.desc())


#def closed_logs():
   # return db.session.query(Maintenance_Logs).filter_by(MaintenanceLog_panel_id=panel_id, status='0').order_by(Maintenance_Logs.posted_date.asc())


@main_blueprint.route('/MaintenanceLogs/#<int:panel_id>/')
def MaintenanceLogs(panel_id):
    open_logs=db.session.query(Maintenance_Logs).filter_by(status='1').order_by(Maintenance_Logs.priority.desc())
    closed_logs=db.session.query(Maintenance_Logs).filter_by(MaintenanceLog_panel_id=panel_id, status='0').order_by(Maintenance_Logs.priority.desc())
    panel_id=panel_id
    return render_template(
        'QR_dataview_logs.html',
        form=AddMaintenanceLog(request.form),
        open_logs=open_logs,
        closed_logs=closed_logs,
        panel_id=panel_id
    )
    
@main_blueprint.route('/NewMaintenanceLog/#<int:panel_id>/', methods=['GET','POST'])
def new_MaintenanceLog(panel_id):
    error=None
    panel_id=panel_id
    form=AddMaintenanceLog(request.form)
    if request.method == 'POST':
        new_MaintenanceLog=Maintenance_Logs(
            form.maintenance_issue.data,
            form.priority.data,
            datetime.datetime.utcnow(),
            '1'
        )
        db.session.add(new_MaintenanceLog)
        db.session.commit()
        flash('Maintenance log created successfully.')
        return redirect(url_for('main.MaintenanceLogs', panel_id=panel_id))
    


@main_blueprint.route('/complete/#<int:MaintenanceLog_id>/', methods=['GET','POST'])
def complete_MaintenanceLog(MaintenanceLog_id):
    error=None
    New_id=MaintenanceLog_id
    form=AddMaintenanceLog(request.form)
    maintenancelog=db.session.query(Maintenance_Logs).filter_by(MaintenanceLog_id=New_id)
    panel_id=maintenancelog.MaintenanceLog_panel_id
    if request.method=='POST':
        maintenancelog.update({"status": "0"})
        maintenancelog.update({"action_taken": f"{form.action_taken.data}"})
        db.session.commit()
        flash('Maintenance log completed.')
        return redirect(url_for('main.MaintenanceLogs', panel_id=panel_id))

@main_blueprint.route('/deleteMaintenancelog/<int:MaintenanceLog_id>/')
def delete_MaintenanceLog(MaintenanceLog_id):
    New_id=MaintenanceLog_id
    maintenancelog=db.session.query(Maintenance_Logs).filter_by(MaintenanceLog_id=New_id)
    panel_id=maintenancelog.MaintenanceLog_panel_id
    maintenancelog.delete()
    db.session.commit()
    flash('The maintenance log was deleted.')
    return redirect(url_for('main.MaintenanceLogs', panel_id=panel_id))





##########################################################################################################################################


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
            
            ##checks if panel exists

            if panel is None:

                error= 'That panel does not exist'
                return render_template('QR_register.html', form=form, error=error)
            
            if panel is not None and panel.name == request.form['panel_name']: #and panel.panel_id == request.form['panel_id'] and panel.project_id == request.form['project_id']:
               
                
                new_QR= QRcode(
                form.panel_id.data,
                form.end_user.data,
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
                error= 'Panel name does not match. This field is case sensitive'
                return render_template('QR_register.html', form=form, error=error)
      
    return render_template('QR_register.html', form=form, error=error)

###use this to view files from emailed link
@main_blueprint.route('/QRlink/<int:panel_id>/')
def QRlink(panel_id):
    qrcode=QRcode.query.filter_by(panel_id=panel_id).first()
   
    panels=Panel.query.filter_by(panel_id=panel_id).first()
    panel_id=panels.panel_id
    PANEL_ID=str(panel_id)
    panel_name=panels.name

    s3_resource=boto3.resource('s3')
    my_bucket=s3_resource.Bucket(S3_BUCKET)
    summaries=my_bucket.objects.filter(Prefix=f'{PANEL_ID}/')
    
    
    return render_template('QR_dataview_Emailed.html', my_bucket=my_bucket, files=summaries, panel_id=panel_id, panel_name=panel_name, )


@main_blueprint.route('/QRfiles/#<int:panel_id>/')
def QRfiles(panel_id):
    qrcode=QRcode.query.filter_by(panel_id=panel_id).first()
    form=SendEmailLink(request.form)
    if qrcode is None: ##idk why i put this shit here
        
        return redirect(url_for('main.login'))
    
    

    panels=Panel.query.filter_by(panel_id=panel_id).first()
    panel_id=panels.panel_id
    PANEL_ID=str(panel_id)
    panel_name=panels.name

    s3_resource=boto3.resource('s3')
    my_bucket=s3_resource.Bucket(S3_BUCKET)
    summaries=my_bucket.objects.filter(Prefix=f'{PANEL_ID}/')
    
    
    return render_template('QR_dataview.html', my_bucket=my_bucket, files=summaries, panel_id=panel_id, panel_name=panel_name, form=form)
 

@main_blueprint.route('/QRemail/<int:panel_id>/', methods=['POST'])
def emailQRlink(panel_id):
    form=SendEmailLink(request.form)
    panels=Panel.query.filter_by(panel_id=panel_id).first()
    panel_name=panels.name
    if request.method== 'POST':
        if form.validate_on_submit():
            msg = Message(subject=f"Link to {panel_name} data ",
                        sender=("main@scanmatics.com"),
                        recipients=[request.form['email']]) 
            msg.body=f'''"https://gentle-refuge-43155.herokuapp.com/QRlink/{panel_id}/" '''
            mail.send(msg)
            flash('Email has been sent')
            return redirect(url_for('main.QRfiles', panel_id=panel_id))


# <a href=f"https://gentle-refuge-43155.herokuapp.com/QRlink/{panel_id}/">here</a>
    
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
            if user is not None and bcrypt.check_password_hash(user.password, request.form['password']) :
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


@main_blueprint.route('/projects/#<int:customer_id>') ##return <int: customer_id>
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

@main_blueprint.route('/QRdelete/<int:panel_id>', methods=['POST'])
def QRdelete(panel_id):
    key=request.form['key']

    panels=Panel.query.filter_by(panel_id=panel_id).first()
    panel_id=panels.panel_id

    s3_resource=boto3.resource('s3')
    my_bucket=s3_resource.Bucket(S3_BUCKET)
    my_bucket.Object(key).delete()

    flash('File deleted successfully')
    return redirect(url_for('main.QRfiles',panel_id=panel_id))

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


@main_blueprint.route('/QRupload/<int:panel_id>/', methods=['POST'])
def QRupload(panel_id):
    file=request.files['file']
    panels=Panel.query.filter_by(panel_id=panel_id).first()
    panel_id=panels.panel_id
    
    PANEL_ID=str(panel_id) #added this
    
    key= f"{PANEL_ID}/"+file.filename


    s3_resource=boto3.resource('s3')
    my_bucket=s3_resource.Bucket(S3_BUCKET)
    my_bucket.Object(file.filename).put(Body=file, Key=key)

    flash('File uploaded successfully')

    return redirect(url_for('main.QRfiles', panel_id=panel_id))


@main_blueprint.route('/QRlinkupload/<int:panel_id>/', methods=['POST'])
def QRlinkupload(panel_id):
    file=request.files['file']
    panels=Panel.query.filter_by(panel_id=panel_id).first()
    panel_id=panels.panel_id
    
    PANEL_ID=str(panel_id) #added this
    
    key= f"{PANEL_ID}/"+file.filename


    s3_resource=boto3.resource('s3')
    my_bucket=s3_resource.Bucket(S3_BUCKET)
    my_bucket.Object(file.filename).put(Body=file, Key=key)

    flash('File uploaded successfully')

    return redirect(url_for('main.QRlink', panel_id=panel_id))







@main_blueprint.route('/reset_password', methods=['GET', 'POST'])
def reset_request():
    form=RequestResetForm(request.form)
    if form.validate_on_submit():
        user=User.query.filter_by(email=request.data).first()
        if user:
            send_reset_email(user)
        
        flash('Check your email for instructions to reset your password')
        return redirect(url_for('main.login'))
    return render_template('reset_request.html', title='Reset Password', form=form)

@main_blueprint.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_token(token):
    user=User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('reset_request'))
    form = ResetPasswordForm(request.form)
    if form.validate_on_submit():
            
        hashed_password=bcrypt.generate_password_hash(form.password.data).decode('utf-8'),####### added.decode(utf-8)
        user.password=hashed_password               
        db.session.commit()
        flash('Your password has been updated.')
        return redirect(url_for('main.login'))
    return render_template('reset_token.html', title='Reset Password',form= form)

def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request',
                  sender='main@scanmatics.com',
                  recipients=[user.email])
    msg.body = f'''To reset your password, visit the following link:
{url_for('reset_token', token=token, _external=True)}
If you did not make this request then simply ignore this email and no changes will be made.
'''
    mail.send(msg)




    
    



