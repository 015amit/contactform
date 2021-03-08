from flask import Flask,render_template,request,flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_mail import Mail, Message
from flask_migrate import Migrate
from threading import Thread
import os

basedir = os.path.abspath(os.path.dirname(__file__))


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///test2.db'
db = SQLAlchemy(app)

app.config['SECRET_KEY'] = 'contact form'

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587 
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')

app.config['MAIL_SUBJECT_PREFIX'] =  '[New Query]'
app.config['MAIL_SENDER'] = 'ADMIN <amitnitt015@gmail.com>'
app.config['ADMIN'] = os.environ.get('ADMIN') 

# db.create_all()
mail = Mail(app)
migrate = Migrate(app,db)


def send_mail_async(app,msg):
    with app.app_context():
        mail.send(msg)

def send_mail(to,sub,template,**kwargs):
    msg = Message(app.config['MAIL_SUBJECT_PREFIX'] + sub,sender=app.config['MAIL_SENDER'],recipients=[to])
    msg.body = render_template(template + '.txt',**kwargs)
    msg.html = render_template(template + '.html',**kwargs)
    thr = Thread(target=send_mail_async,args=(app,msg))
    thr.start()
    return thr

class Contacts(db.Model):
    __tablename__ = 'contact'
    Sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=False, nullable=False)
    email = db.Column(db.String(120), unique=False, nullable=False)
    subject = db.Column(db.String(80), unique=False, nullable=False)
    message = db.Column(db.String(200), unique=False, nullable=False)
    date = db.Column(db.String(12), unique=True, nullable=True)

    def __repr__(self):
        return '<Contacts %r>' % self.name

@app.route("/")
def index():
    return render_template("contact.html")


@app.route("/result", methods=['POST', 'GET'])
def result():
    if request.method == "POST":
        Name = request.form.get("Name")
        Email = request.form.get("email")
        Subject = request.form.get("Subject")
        Message = request.form.get("message")

        en = Contacts(name= Name, email=Email, subject=Subject, message=Message, date=datetime.now()  )
        db.session.add(en)
        db.session.commit()
        send_mail(app.config['ADMIN'],'query','mail/query',name=Name,email=Email,subject=Subject,message=Message)
        flash('Form submitted')
    return render_template("contact.html")

if __name__ == '__main__':
    app.run(debug=True)





