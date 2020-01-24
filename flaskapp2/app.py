from flask import Flask,render_template,request,redirect,session,jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
#from flask_bcrypt import Bcrypt
from flask_login import LoginManager
import json

app=Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///test8.db'
db=SQLAlchemy(app)
app.secret_key = "abc" 
#bcrypt=Bcrypt(app)
loginmanager=LoginManager(app)

usser=1
class User(db.Model):
	id = db.Column(db.Integer,primary_key=True)
	username=db.Column(db.String(64),unique=True,nullable=False)
	email=db.Column(db.String(64),unique=True,nullable=False)
	password=db.Column(db.String(64),nullable=False)
	level= db.Column(db.Integer,default=0)
	tasks=db.relationship('Todo',backref='author', lazy=True)

	def __repr__(self):
		return '<User {}>'.format(self.id)
	

class Todo(db.Model):

	id = db.Column(db.Integer,primary_key=True)
	content = db.Column(db.String(200),nullable=False)
	completed = db.Column(db.Integer,default=0)
	date_created = db.Column(db.DateTime,default=datetime.utcnow)
	status = db.Column(db.String(200))
	date_finished = db.Column(db.DateTime,default=datetime.utcnow)
	user_id=db.Column(db.Integer,db.ForeignKey('user.id'))

	def __repr__(self):
		return '<Task {}>'.format(self.id)

@app.route('/register', methods=['POST','GET'])
def register():
	if(request.method=='POST'):
		username=request.form['usrname']
		passs=request.form['pass']
		lev=request.form['levl']
		email=passs+"@g.com"
		userr=User(username=username,password=passs,email=email,level=lev)
		db.session.add(userr)
		db.session.commit()
		return redirect('/login')
	else:
		return render_template('register.html')

@app.route('/login', methods=['GET','POST'])
def login_user():
	if(request.method=='POST'):
		username=request.form['usrname']
		passs=request.form['pass']
		user=User.query.filter(User.username==username).first()
		usser=user.id+1
		if(user.password==passs):
			tasks=Todo.query.order_by(Todo.date_created).all()
			if(user.level!=0):
				session['response']=user.username
				session['response2']=user.level
				return render_template('index.html',tasks=tasks,user=user)
			else:
				session['response']=user.username
				session['response2']=user.level
				return render_template('indexr.html',tasks=tasks,user=user)
			#return redirect('/')
		else:
			return redirect('/login')
	else:

		return render_template('login.html')
@app.route('/', methods=['POST','GET'])

def index():
	if(request.method=='POST'):
		iplist=request.get_json()
		task_content=request.form['content']
		fin_date=request.form['findate']
		findate = datetime.strptime(fin_date, '%Y-%m-%d')
		option=request.form['progres']
		print(option)
		iplist2={"task_content":task_content,"option":option}
		new_task=Todo(content=task_content,status=option,date_finished=findate.date())
		#try:
		db.session.add(new_task)
		db.session.commit()
		session['response3']=iplist2
#		return jsonify({"you sent" : iplist2}) , 201
		return redirect('/')
		#except:
		#	return "There was an error"
		
			
	else:
		tasks=Todo.query.order_by(Todo.date_created).all()
		usernam=session['response']
		user=User.query.filter(User.username==usernam).first()
		jsontype=session['response3']
		print(jsontype)
		return render_template('index.html',tasks=tasks,user=user)
@app.route('/delete/<int:id>')
def delete(id):
	task_to_delete=Todo.query.get_or_404(id)
	db.session.delete(task_to_delete)
	db.session.commit()
	return redirect('/')
@app.route('/update/<int:id>', methods=['POST','GET'])
def update(id):
	task=Todo.query.get_or_404(id)
	if(request.method=='POST'):
		task.content=request.form['newcontent']
		fin_date=request.form['findate']
		findate = datetime.strptime(fin_date, '%Y-%m-%d')
		task.date_finished = findate.date() 
		task.status=request.form['progres']
		
		#new_task=Todo(content=task_content,date_finished=fin_date,status=option)
		#new_task2=Todo(content=tasknew)
		#db.session.add(new_task2)
		db.session.commit()
		return redirect('/')	
	else:
		return render_template('update.html',task=task)
@app.route('/finished')
def getfinishedjobs():
	new_dict={}
	tasks=Todo.query.filter(Todo.status=="Finished").all()
	for i in range(len(tasks)):
		#
		new_dict["task"+str(i)]=tasks[i].content
		#my_json={"title"+tasks[i].id:tasks[i].content}
	to_json=json.dumps(new_dict)	
#	return to_json
	return render_template('finishedjobs.html',tasks=tasks)
@app.route('/overdue')
def getoverduejobs():
	new_dict={}
	tasks=Todo.query.filter(Todo.date_finished<=datetime.now()).all()
	for i in range(len(tasks)):
		#
		new_dict["task"+str(i)]=tasks[i].content
		#my_json={"title"+tasks[i].id:tasks[i].content}
	to_json=json.dumps(new_dict)	
#	return to_json
	return render_template('overduejobs.html',tasks=tasks)
@app.route("/due")
def getjobs2():
		#if edate in request.args:
			#return "helloo"
		new_dict={}
		edate=request.args.get('duedate')
		eedate=datetime.strptime(edate, '%Y-%m-%d')
		tasks=Todo.query.filter(Todo.date_finished==eedate).all()
		for i in range(len(tasks)):
		#
			new_dict["task"+str(i)]=tasks[i].content
		#my_json={"title"+tasks[i].id:tasks[i].content}
		to_json=json.dumps(new_dict)	
	#	return to_json
		return render_template('duedate.html',tasks=tasks,edate=eedate)
		#return edate
	

@app.route("/getByExpected" ,methods=['POST','GET'])
def getjobs():
	if request.method == 'GET':
		return "ECHO: GET\n"

	elif request.method == 'POST':
		return "ECHO: POST\n"

	if(request.method=="POST"):
		edate=request.args['edate']
		eedate=datetime.strptime(edate, '%Y-%m-%d')
		tasks=Todo.query.filter(Todo.date_finished==eedate).all()
		return render_template('duedate.html',tasks=tasks,edate=eedate)
	elif(request.method == 'GET'):
		edate=request.args.get('duedate')
		eedate=datetime.strptime(edate, '%Y-%m-%d')
		tasks=Todo.query.filter(Todo.date_finished==eedate).all()
		return render_template('duedate.html',tasks=tasks,edate=eedate)
	else:
		pass

if __name__=="__main__":
	app.run(debug=True)
