"""updates database with questions
update 5 questions at a time"""
from flask import (Blueprint,request,session,
                   redirect,url_for,flash,render_template,g)
from sukuu.firestoreModels1 import db
import datetime as dt
import functools
bp=Blueprint('testupdate',__name__)

def login_required(func):
    @functools.wraps(func)
    def wrapper(**kw):
        #global user_id
        if session.get('user_id'):
            #user_id=session.get('user_id')
            return func(**kw)
        else:
            flash("you need to login to create/add questions")
            return redirect(url_for('auth.login'))

    return wrapper

@bp.route('/testupdate', methods=("POST","GET"))
@login_required
def updateTest():
    if request.method=="POST":
        data=None
        data=request.get_json(silent=True)
        msg='error ocurred while uploading questions'
        #d_s=db.collection('permission').document(
            #'testupdate').get([data.user_id])
        #if d_s.exists:
        if data:
            data['user_id']=session.get('user_id')
            if not data.get('test_id',None):
                f,_=str(dt.datetime.today().timestamp()).split('.')
                data['test_id']="TEST{}".format(f[4:])
            data['user_id']=session.get('user_id')
            data.pop("",None)
            if not data.get('num_q',None):
                data['num_q']=len(data['q'])
            db.collection('tests').document(data['test_id']).set(data,True)
            msg=' All questions saved'
            return 'Test: '+data['test_id']+msg
        return msg
    return render_template("makeTest.html")
@bp.route('/testupdate/edit/<test_id>')
@login_required
def editTest(test_id):
    l=('creator','title','nodate','duration','stime','etime','nxt_num')
    snap=db.collection('tests').document(test_id).get(l)
    if snap._data:
        g.data=snap._data
    else:
        return redirect(url_for('home.index'))
    return render_template("editTest.html")
##@bp.route('/test/<meth>', methods=("POST",))
##def getTest(meth=None):
##    test_id=request.form.get('test_id')
##    s_id=request.form.get('s_id')
##    if test_id:
##        doc=db.collection("tests").document(test_id).get()
##        if doc.exists:
##            #do_sth()
##            pass
##    
##    return redirect(url_for('home.index'))

