from flask import (Blueprint,render_template,request,jsonify,
                   session,g,redirect,url_for)
from sukuu.firestoreModels1 import User,get_db,db
import datetime as dt
from google.cloud import firestore
from google.cloud.firestore_v1.field_path import render_field_path


bp=Blueprint('story',__name__,url_prefix='/confessions')
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
                if g.user:
                    if d.get('u',None)==g.user.user_id:
                        d['created_by_current_user']=True
                        d['fullname']='You'
                    s=snap.reference.parent.where(
                        'c','==','l').where(
                        render_field_path([str(r[p.index(i)]),'u']),
                        'array_contains',g.user.user_id).select(
                            ['c']).limit(1).stream()
                    for doc in s:
                        d['user_has_upvoted']=True
                else:
                    d['user_has_upvoted']=False   
                cdata.append(d)
            except KeyError:
                ccount=r[p.index(i)]
                s=snap.reference.parent.where(
                    'c','==','c').where(
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

def getComSize(d):
    sz=0
    for i,v in d.items():
        sz+=(len(i)+1)
        if isinstance(v,str):
            sz+=(len(v)+1)
        else:
            sz+=8
    return sz
@bp.route('/',defaults={'aid':'first'})
@bp.route('/<aid>')
def getarticle(aid):
    c_r=db.collection('confessions')
    snap=c_r.document(aid).get()
    if not snap._data:
        snap=c_r.document('first').get()
    g.data=snap.to_dict()
    g.data['id']=snap.id
    d_s=c_r.where('tags','array_contains_any',snap._data['tags']).select(
        ['title','id']).limit(5).stream()

    d=[]
    doc=None
    for doc in d_s:
        d.append(doc.to_dict())
    else:
        if doc is None:
            snap=c_r.document('first').get(['tags'])
            d_s=c_r.where('tags','array_contains_any',snap._data['tags']).select(
            ['title','id']).limit(5).stream()
            for doc in d_s:
                d.append(doc.to_dict())
            
            
    if 'u' not in g:
        g.u=['anonymous','anonymous']
    if 'tcom_n' not in g:
        g.tcom_n=""
        
    g.other=d  
    return render_template('confessblog.html',user=g.user)

@bp.route('/userquestions/',defaults={'aid':'first'})
@bp.route('/userquestions/<aid>')
def getquestion(aid):
    c_r=db.collection('userquestions')
    if aid=="first":
        s=db.collection('userquestions').list_documents(1)
        for doc_ref in s:
            snap=doc_ref.get()
            break
        else:
            c_r=db.collection('confessions')
            snap=c_r.document('first').get()        
    else:
        c_r=db.collection('userquestions')
        snap=c_r.document(aid).get()
    if not snap._data:
        snap=c_r.document('first').get()
    g.data=snap.to_dict()
    g.data['id']=snap.id
    d_s=c_r.where('tags','array_contains_any',snap._data['tags']).select(
        ['title','id']).limit(5).stream()

    d=[]
    doc=None
    for doc in d_s:
        d.append(doc.to_dict())
    else:
        if doc is None:
            c_r=db.collection('confessions')
            snap=c_r.document('first').get(['tags'])
            d_s=c_r.where('tags','array_contains_any',snap._data['tags']).select(
            ['title','id']).limit(5).stream()
            for doc in d_s:
                d.append(doc.to_dict())
    if 'u' not in g:
        g.u=['anonymous','anonymous']
    if 'tcom_n' not in g:
        g.tcom_n=""
        
    g.other=d 
    return render_template('questionblog.html',user=g.user)
    
    
    
@bp.route('/post/<sth>',methods=('POST',"GET"))
def writequestion(sth):
    if sth=="question":
        category="userquestions"
        route='story.getquestion'
    else:
        category='confessions'
        route='story.getarticle'
        
    if request.method=="POST":
        c_r=db.collection(category)
        data=request.form.copy()
        if g.user is not None:
            if not data.get('anon') and 'nick' in g.user.__dict__:
                data['u']=[g.user.nick,g.user.user_id]        
        if not data.get('u'):
            data['u']=['anonymous','']
        if isinstance(data.get('tags'),str):
            data['tags']=data['tags'].split(',')
        data['dt']=dt.date.today().isoformat()
        aid=c_r.add(data)[1].id
        return redirect(url_for(route,aid=aid))
    return render_template('addquestion.html')

@bp.route('/comments/<aid>',methods=('GET','POST'))
def commentsf(aid):
    #c=session.get('paper').split('_')
    q=category=request.args.get('q')
    if not q:
        category=q='confessions'
    doc_ref=db.collection(category).document('data').collection(
        'comments').document(aid)
    if request.method=="POST":
        d=request.get_json()
        qcount=d.pop('q',None)
        if qcount:
            qcount=str(qcount)
        l=('pings','modified','attachments','created_by_current_user')
        for i in l: 
            d.pop(i,None)
        if isinstance(d['id'],str):
            if 'c' in d['id']:
                d['id']=d['id'].lstrip('c')
        if g.user:
            d['u']=g.user.user_id
            d['fullname']=g.user.nick
        d_r=doc_ref
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
            n_d.set({'s':True,str(n):d,'n':n,'c':'c','aid':aid,
                             'q':q,'cA':[str(n)],
                     'space':spc})
            
        if snap._data:
            if sz < snap._data['space']:
                saveCom(snap)
                      
            else:
                s=d_r.parent.where('q','==',q).where('s','==',True).where(
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
            d_r.set({'s':True,'aid':aid,
                     str(1):d,'n':1,'c':'c','q':q,'cA':['1'],'space':spc})
        if cid < n and n != 1:
                return getcomments(d_r,cid,n-cid+1)
        else:
            return jsonify(['ok'])
    if doc_ref.get(['n'])._data:
        return getcomments(doc_ref)
    return jsonify(["no comments"])
@bp.route('/comments/likes/<aid>',methods=['POST'])    
def likesf(aid):
    d=request.get_json()
    q=request.args.get('q')
    qcount=d.pop('q',None)
    if qcount:
        qcount=str(qcount)
    c_ref=db.collection(q).document('data').collection('comments')
    if isinstance(d['id'],str) and 'c' in d['id']:
        d['id']=d['id'].lstrip('c')
    s=c_ref.where('c','==','c').where(
            'aid','==',aid).where(
                'cA','array_contains',str(d['id'])).limit(1).stream()
    for doc in s:
        doc.reference.update({render_field_path(
                [str(d['id']),'upvote_count']):firestore.Increment(1)})
    
    s=c_ref.where('c','==','l').where(
        'aid','==',aid).limit(1).stream()
    for doc in s:
        d_r=doc.reference
        d_r.update({str(d['id']):{'n':firestore.Increment(1),'u':
                                    firestore.ArrayUnion([g.user.user_id])}})        
        break
    else:
        d_r=c_ref.document()    
        d_r.set({'c':'l','aid':aid,
                    str(d['id']):{'n':firestore.Increment(1),
                                  'u':firestore.ArrayUnion([g.user.user_id])}})
    return 'ok'


##@bp.route('/comments/<aid>',methods=['GET','POST'])
##def commentsf(aid):
##    #cid confession id
##    category=request.args.get('q')
##    if not category:
##        category='confessions'
##    if request.method=="POST":
##        d=request.get_json()
##        l=['pings','modified','attachments','created_by_current_user']
##        for i in l: 
##            d.pop(i,None)
##        if isinstance(d['id'],str):
##            if 'c' in d['id']:
##                d['id']=d['id'].lstrip('c')
##        
##        if d['anon']:
##            d['fullname']='anonymous'
##        else:
##            d['fullname']=g.user.nick
##            d['u']=g.user.user_id
##            
##        d_r=db.collection(category).document('data').collection(
##            'comments').document(aid)
##        d['created']=dt.date.today().isoformat()    
##        snap=d_r.get(['n','space'])
##        n=1
##        com_n=int(d['id'])
##        sz=getComSize(d)
##        spc=1000000-48-sz
##        def saveCom(doc):
##            n=doc.get('n')+1
##            d.update({'id':n})
##            doc.reference.update({render_field_path([str(n)]):d,
##                            'space':doc._data['space']-sz,
##                        'n':firestore.Increment(1),
##                        'cA':firestore.ArrayUnion([str(n)])})
##        def newDoc(o_r):
##            o_r.update({'s':False})
##            n_d=o_r.parent.document()
##            snap=o_r.get(['n'])
##            n=snap.get('n')+1
##            d.update({'id':n})
##            n_d.set({'s':True,str(n):d,'n':n,'c':'c',
##                             'aid':aid,'cA':[str(n)],
##                     'space':spc})
##            
##        if snap._data:
##            if sz < snap._data['space']:
##                saveCom(snap)
##                      
##            else:
##                s=d_r.parent.where('aid','==',aid).where('s','==',True).where(
##                    'c','==','c').select(['space','n']).stream()
##                for doc in s:
##                    if sz<doc._data['space']:
##                        saveCom(doc)
##                    else:
##                        newDoc(doc.reference)
##                    break
##                        
##                else:
##                    newDoc(d_r)            
##        else:
##            d['id']=1
##            d_r.set({'s':True,
##                     str(1):d,'n':1,'c':'c','aid':aid,'cA':['1'],'space':spc})
##        db.collection(category).document(aid).update({
##            'tcom_n':firestore.Increment(1)})
##        if com_n < n and n != 1:
##                return getcomments(d_r,com_n,n-(com_n+1))
##        else:
##            return jsonify(['ok'])
##    s=db.collection(category).document('data').collection(
##        'comments').where(
##            'c','==','c').where('aid','==',aid).select(
##                ['n']).limit(1).stream()
##    for d in s:
##        return getcomments(d.reference)
##    else:
##        return jsonify([])