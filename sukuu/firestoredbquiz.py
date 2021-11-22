from flask import (Blueprint,render_template,request,jsonify,
                   session,g,redirect,url_for,make_response,flash)
from sukuu.firestoreModels1 import User,get_db
import datetime as dt
from google.cloud import firestore
from google.cloud.firestore_v1.field_path import render_field_path
qcount=1
qdata={}
cdata=[]
ccount=1
db=get_db()
bp=Blueprint('queryquestions',__name__,url_prefix='/education')
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
        l.append(render_field_path(['section_A',str(i)]))
    snap=doc_ref.get(l)
    if not snap.exists:
        doc_ref=doc_ref.parent.document('2013')
        snap=doc_ref.get(l)
        if not snap.exists:
            doc_ref=get_db().collection('shsSocial Studies').document('2013')
            snap=doc_ref.get(l)
    try:
        snap.get(render_field_path(['section_A']))
    except KeyError:
        if doc_ref.get(['q_c'])._data:
            n_doc=doc_ref.parent.document(
                doc_ref.get(['q_c']).get('q_c'))
            return qc(n_doc,q)
        else:
            return qdata
    for i in range(q,q+z):
        try:
            qcount=i
            qd=snap.get(
                render_field_path(['section_A',str(i)]))
            qdata.update({str(i):qd})
        except KeyError:
            if doc_ref.get(['q_c'])._data:
                n_doc=doc_ref.parent.document(
                        doc_ref.get(['q_c']).get('q_c'))
                d=(q+z)-qcount
                
                return qc(n_doc,i,d)
            else:
                qcount-=1
                return qdata
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
        

@bp.route('/getquestions/<level>/<subject>/<year>/',methods=["GET","POST"])
def getquestions(level,subject,year):
    category=level+subject
    doc_ref=db.collection(category).document(year)
    p=None
    num_q=None
    
    if session.get(level+'_'+subject+'_'+year):
        p,num_q=session.get(level+'_'+subject+'_'+year).split("_")
        num_q=int(num_q)
    if not num_q:
        num_q=doc_ref.get([render_field_path(['num_q'])]).get(
                    render_field_path(['num_q']))
    if request.method=="POST":
        data=request.get_json()
        if data:
            category=level+'_'+subject
            g.user.save_answer(level+'_'+subject,year,'section_A',data,num_q)
            return ""
            
        
    q=int(request.args.get('q'))
    
    if q:
        resp=make_response(qc(doc_ref,q))
        session[level+'_'+subject+'_'+year]=str(qcount)+"_"+str(num_q)
        return resp
    resp=make_response(qc(doc_ref))
    session[level+'_'+subject+'_'+year]=str(qcount)+"_"+str(num_q)
    return resp
@bp.route('/')
def ques():
    l=request.args.get('l')
    s=request.args.get('s')
    y=request.args.get('y')
    category=l+s
    doc_ref=db.collection(category).document(y)
    snap=doc_ref.get(['section_A'])
    if not snap.exists:
        y='2013'
        doc_ref=doc_ref.parent.document(y)
        snap=doc_ref.get(['section_A'])
        if not snap.exists:
            l='shs'
            s='Social Studies'
            doc_ref=get_db().collection(l+s).document(y)        
    f_s=doc_ref.get(['format'])
    if f_s._data:
        g.setdefault('math',True)
    p=None
    num_q=None
    n_num_q=None
    if session.get(l+'_'+s+'_'+y):
        p,num_q=session.get(l+'_'+s+'_'+y).split("_")
        num_q=int(num_q)
        p=int(p)
    
    doc=doc_ref.get([render_field_path(['num_q'])])
    if doc._data:
        n_num_q=doc.get(render_field_path(['num_q']))
        if num_q != n_num_q:
            num_q=n_num_q
    if p:        
        g.setdefault('questions',qc(doc_ref,p))
        session[l+'_'+s+'_'+y]=str(qcount)+"_"+str(num_q)
    else:
        g.setdefault('questions',qc(doc_ref))
        session[l+'_'+s+'_'+y]=str(qcount)+"_"+str(num_q)
    session.pop('sub',None)
    session['sub']=doc_ref.path
    session['paper']=l+'_'+s+'_'+y
    g.user.subref(doc_ref.path)
    g.setdefault('answers',g.user.getAnswers(l+'_'+s,y))
    g.setdefault('max',num_q)
    g.setdefault('subject',s)
    g.setdefault('year',y)
    return render_template('ques.html')
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
    cdata=[]
    r=range(q,q+z)
    for i in r:
        p.append(render_field_path([str(i)]))
    def getaddcom(p,snap,r):
        #global cdata
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