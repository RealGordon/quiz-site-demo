from flask import (Blueprint,request,render_template,abort,
                    session,g,redirect,url_for,make_response,
                   get_flashed_messages)
from sukuu.firestoreModels1 import User

auth=Blueprint('auth',__name__)

@auth.route('/login/form',methods=("GET","POST"))
def login():
    g.errors={}
    redirect_el=False
    if request.method=="POST":
        t=session.get('logintrial')
        if t:
            if int(t)>15:
                abort(404)
        data=request.form.copy()
        user=None
        
        if data['formtype']=="LogIn":
            if data['email'] and data['pwd']:
                user=User.getdbUser(g,
                    email=data['email'],pwd=data['pwd'],e=data['meth'])             

        else:
            user=User(data=data)        
        if user and user.user_id:        
            session['user_id']=user.user_id
            if request.form.get('redirect'):
                return redirect(request.form.get('redirect'))
            return redirect(url_for('home.index'))

        else:
            #g.setdefault('error',user.errors.get('account',None))
            t=session.get('logintrial')
            if t:
                session['logintrial']=str(int(t)+1)
            else:
                session['logintrial']=str(1)
    for m in get_flashed_messages():
        g.errors.update(account=m)
    if request.args.get('q'):
        redirect_el=True
    return render_template('login.html',redirect_el=redirect_el)
    
        
    
        
@auth.route('/fsg35ef8.txt')
def sitecrawler():
    resp=make_response("   ")
    resp.mimetype = 'text/plain'
    return resp
@auth.route('/facebooklogin',methods=["POST"])
def facebooklogin():
    if request.method=="POST":
        user=User()
        data=request.get_json()
        if data:
            if user.getFacebookUser(data['userID'],data['accessToken']):
                if not user.old_user_status():
                    user.save_new_user()  
                g.setdefault('user',user)
                session.setdefault('user_id',data['userID'])          
                return "1. facebook login success"
            else:
                "1.facebook login failure"
            
        uid=request.args.get('userID',None)
        token=request.args.get('accessToken',None)
        if uid and token: 
            if user.getFacebookUser(uid,token):
                if not user.old_user_status():
                    user.save_new_user()  
                g.setdefault('user',user)
                session.setdefault('user_id',uid)          
                return "2. login success facebook"
            else:
                return "2.facebook login failure"
        
        return "login failure"

@auth.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('logintrial',None)
    session.pop('sub',None)
    return redirect(url_for('home.index'))
    
