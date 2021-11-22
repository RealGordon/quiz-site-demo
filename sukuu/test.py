from flask import (Blueprint,render_template,request,jsonify,
                   session,g,redirect,url_for,make_response,flash)
from sukuu.testModel import User,get_db
import datetime as dt
from google.cloud import firestore
from google.cloud.firestore_v1.field_path import render_field_path
qcount=1
qdata={}
cdata=[]
ccount=1
db=get_db()
bp=Blueprint('testquestions',__name__,url_prefix='/test')
def qc(doc_ref,q=1,z=10):
    """ query content of document"""
    global qcount,qdata
    l=[]
    if q!=1:
        c=divmod(q,10)
        if c[1]==0:
            q=(c[0]*10)-9
        else:
            if c[0]==0:
                q=1
            else:
                q=(c[0]*10)+1            
    
    for i in range(q,q+z):  
        l.append(render_field_path([str(i)]))
    else:
        l.append('q_c')    
    snap=doc_ref.get(l)
    if not snap.exists:
        return qdata
    if snap._data:
        qdata.update(snap._data)
        if qdata.get('q_c',None):
            qdata.pop('q_c')
        l_num=(list(qdata).sort())[-1]
        qcount=int(l_num)
        d=(q+z)-qcount
        if d>1:
            if snap._data.get('q_c',None):
                n_doc=doc_ref.parent.document(
                            snap.get('q_c'))
                return qc(n_doc,qcount+1,d)
    return qdata

def getComSize(d):
    sz=0
    for i,v in d.items():
        sz+=(len(i)+1)
        if isinstance(v,str):
            sz+=(len(v)+1)
        else:
            sz+=8
    return sz

@bp.before_app_request
def load_login_user():
    user_id=session.get('user_id')
    if user_id is None:
        g.user=None        
    else:
        user=User.getdbUser(g,user_id=user_id)
        if user:
            g.setdefault('user',user)
@bp.before_request
def load_sub_ref():
    global qdata,cdata,ccount
    qdata={}
    cdata=[]
    ccount=1
    if g.user is None:
        flash('you need to login/signup to access this site')
        return redirect(url_for('auth.login'))
    if session.get('sub'):
        if g.user:
            g.user.subref(session.get('sub'))
        

@bp.route('/getquestions/<test_id>',methods=("GET","POST"))
def getquestions(test_id):
    doc_ref=db.collection('tests').document(test_id)
    p=None
    num_q=None
    
    if session.get(test_id):
        p,num_q=session.get(test_id).split("_")
        num_q=int(num_q)
    if not num_q:
        num_q=doc_ref.get([render_field_path(['num_q'])]).get(
                    render_field_path(['num_q']))
    if request.method=="POST":
        data=request.get_json()
        if data:
            g.user.save_answer(test_id,data,num_q)
            return ""
            
        
    q=int(request.args.get('q'))    
    if q:
        resp=make_response(qc(doc_ref,q))
        session[test_id]=str(qcount)+"_"+str(num_q)
        return resp
    resp=make_response(qc(doc_ref))
    session[test_id]=str(qcount)+"_"+str(num_q)
    return resp
@bp.route('/form',methods=("POST",))
def get_test():
    test_id=request.form.get('test_id')
    if not test_id:
        return redirect(url_for('home.index'))
    doc_ref=db.collection('tests').document(test_id)
    snap=doc_ref.get()
    if not snap.exists:
        g.message=test_id+" does not exist"
        return redirect(url_for('home.index'))        
    if snap._data.get('format',None):
        g.setdefault('math',True)
    g.data=snap._data
    p=None
    num_q=None
    n_num_q=None
    if session.get(test_id):
        p,num_q=session.get(test_id).split("_")
        num_q=int(num_q)
        p=int(p)
    
    if snap._data.get('num_q',None):
        n_num_q=snap.get('num_q')
        if num_q != n_num_q:
            num_q=n_num_q
    if p:        
        g.setdefault('questions',qc(doc_ref,p))
        session[test_id]=str(qcount)+"_"+str(num_q)
    else:
        g.setdefault('questions',qc(doc_ref))
        session[test_id]=str(qcount)+"_"+str(num_q)
    session.pop('sub',None)
    session['sub']=doc_ref.path
    g.setdefault('max',num_q)
    #session['paper']=l+'_'+s+'_'+y
    #g.user.subref(doc_ref.path)
    #g.setdefault('answers',g.user.getAnswers(l+'_'+s,y))
    #g.setdefault('subject',s)
    #g.setdefault('year',y)
    return render_template('testques.html')
def getlikes(r,n):
    data={}
    s=r.where('q','==',qcount).where(
        'c','==','likes').stream()
    for d in s:
        data['n']=d.get(render_field_path([str(n),'n']))
    s=r.where('q','==',qcount).where(
        'c','==','likes').where(render_field_path([n,'u']),
                                'array_contains',g.user.user_id).stream()
    for d in s:
        if d.exists:
            data['s']=True
            break
    else:
        data['s']=False
    return data

def getcomments(doc_ref,q=1,z=20):
    p=[]
    r=range(q,q+z)
    for i in r:
        p.append(render_field_path([str(i)]))
    def getaddcom(p,snap,r):
        global cdata
        for i in p:
            try:
                d=snap.get(i)
                if d['u']==g.user.user_id:
                    d['created_by_current_user']=True
                    d['fullname']='You'
                s=snap.reference.parent.where(
                    'c','==','l').where('q','==',qcount).where(
                        render_field_path([str(r[p.index(i)]),'u']),
                        'array_contains',g.user.user_id).select(
                            ['c']).limit(1).stream()
                for doc in s:
                    d['user_has_upvoted']=True
                cdata.append(d)
            except KeyError:
                ccount=r[p.index(i)]
                s=snap.reference.parent.where(
                    'c','==','c').where('q','==',qcount).where(
                        'cA','array_contains',str(ccount)).select(
                            p[p.index(i):]).limit(1).stream()
                for doc in s:
                    r=r[p.index(i):]
                    return getaddcom(p[p.index(i):],doc,r)
        return None
    snap=doc_ref.get(p)
    if snap._data:
        getaddcom(p,snap,r)

            
    return jsonify(cdata)
    


@bp.route('/comments/',methods=['GET','POST'])
def commentsf():
    c=session.get('paper').split('_')
    global qcount
    if request.method=="POST":
        d=request.get_json()
        qcount=d.pop('q',None)
        if qcount:
            qcount=str(qcount)
        l=['pings','modified','attachments','created_by_current_user']
        for i in l: 
            d.pop(i,None)
        if isinstance(d['id'],str):
            if 'c' in d['id']:
                d['id']=d['id'].lstrip('c')
        d['u']=g.user.user_id
        d['fullname']=g.user.nick
        d_r=g.user.sub_ref.collection('comments').document('q_'+qcount)
        d['created']=dt.date.today().isoformat()    
        snap=d_r.get(['n','space'])
        n=1
        cid=int(d['id'])
        sz=getComSize(d)
        spc=1000000-48-sz
        def saveCom(doc):
            n=doc.get('n')+1
            d.update({'id':n})
            doc.reference.update({render_field_path([str(n)]):d,
                            'space':doc._data['space']-sz,
                        'n':firestore.Increment(1),
                        'cA':firestore.ArrayUnion([str(n)])})
        def newDoc(o_r):
            o_r.update({'s':False})
            n_d=o_r.parent.document()
            snap=o_r.get(['n'])
            n=snap.get('n')+1
            d.update({'id':n})
            n_d.set({'s':True,str(n):d,'n':n,'c':'c',
                             'q':qcount,'cA':[str(n)],
                     'space':spc})
            
        if snap._data:
            if sz < snap._data['space']:
                saveCom(snap)
                      
            else:
                s=d_r.parent.where('q','==',qcount).where('s','==',True).where(
                    'c','==','c').select(['space','n']).stream()
                for doc in s:
                    if sz<doc._data['space']:
                        saveCom(doc)
                    else:
                        newDoc(doc.reference)
                    break
                        
                else:
                    newDoc(d_r)            
        else:
            d['id']=1
            d_r.set({'s':True,
                     str(1):d,'n':1,'c':'c','q':qcount,'cA':['1'],'space':spc})
        if cid < n and n != 1:
                return getcomments(d_r,cid,n-cid+1)
        else:
            return jsonify(['ok'])
    qcount=request.args.get('q')
    s=g.user.sub_ref.collection('comments').where(
            'c','==','c').where('q','==',qcount).select(
                ['n']).limit(1).stream()
    for d in s:
        return getcomments(d.reference)
    else:
        return jsonify(["no comments"])
    
    
            
    
@bp.route('/comments/likes',methods=['POST'])    
def likesf():
    d=request.get_json()
    qcount=d.pop('q',None)
    if qcount:
        qcount=str(qcount)

    if isinstance(d['id'],str) and 'c' in d['id']:
        d['id']=d['id'].lstrip('c')
    s=g.user.sub_ref.collection('comments').where(
        'c','==','c').where(
            'q','==',qcount).where(
                'cA','array_contains',str(d['id'])).limit(1).stream()
    for doc in s:
        doc.reference.update({render_field_path(
                [str(d['id']),'upvote_count']):firestore.Increment(1)})
    
    s=g.user.sub_ref.collection('comments').where(
        'c','==','l').where('q','==',qcount).limit(1).stream()
    for doc in s:
        d_r=doc.reference
        d_r.update({str(d['id']):{'n':firestore.Increment(1),'u':
                                    firestore.ArrayUnion([g.user.user_id])}})        
        break
    else:
        d_r=g.user.sub_ref.collection('comments').document()    
        d_r.set({'c':'l','q':qcount,
                    str(d['id']):{'n':firestore.Increment(1),'u':
                                    firestore.ArrayUnion([g.user.user_id])}})
    return 'ok'

    
@bp.route('/answers',methods=('POST',))
def shared_answers():
    q=request.form['q']
    o=request.form['o']
    sec='section_A'
    d=g.user.sub_ref.get([render_field_path([sec,q,'a'])])
    if d._data:
        return "no"
    else:
        g.user.sub_ref.update({render_field_path([sec,q,'a']):
                               {'o':o,'u':[g.user.nick,g.user.user_id]}})
        return "ok"