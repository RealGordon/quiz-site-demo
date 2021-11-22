from flask import (Blueprint,request,session,g)
import datetime as dt
from google.cloud import firestore
from google.cloud.firestore_v1.field_path import render_field_path
import smtplib
import os
PASSWORD=os.environ["PASSWORD"]
WEB_EMAIL=os.environ["WEB_EMAIL"]
DEV_EMAIL=os.environ["DEV_EMAIL"]
from . import settings
if settings.SUKUU_LOCAL:
    db=firestore.Client.from_service_account_json(settings.JSON_CREDENTIALS)
else:
    db=firestore.Client()
bp=Blueprint('mail',__name__,url_prefix='/mailing')
def getSize(d):
    sz=0
    for i in d:
        sz+=(len(i)+1)
    return sz
@bp.route('/core')
def mcore():
    err=dt.datetime.today().isoformat()
    today=dt.date.today()
    dy=today.isoformat()
    l=['Social Studies','INT SCIENCE']
    curr=l[0]
    #day=divmod(today.day,2)[1]
    #if day==0:
        #curr=l[0]
    #else:
        #curr=l[1]

    a_q=db.collection('mailing').document('shs').collection(
        'questions').document(curr).get(['active'])
    mail_errors=[]
    d=db.collection('users').document('new_users').get()
    if d._data:
        L=['Social Studies','Mathematics Core','INT SCIENCE']
        u=d.get('u')
        p=d.get('p')
        n=d.get('n')
        d.reference.update({'u':firestore.ArrayRemove(u),
                'n':firestore.ArrayRemove(n),
                'p':firestore.ArrayRemove(p)})
        for sj in L:
            db.collection('mailing').document('shs'+sj).collection(
                'questions').document('q_1').set({'sj':sj,'q':1,
                    'n_u':firestore.ArrayUnion(u),
                    'n':firestore.ArrayUnion(n)},True)
        
        if not a_q.get('active').count(1):
            a_q.reference.update({'active':firestore.ArrayUnion([1])})
        smtpObj = smtplib.SMTP('smtp.gmail.com', 587)
        ch=smtpObj.ehlo()
        if ch[0]==250:
            ch=smtpObj.starttls()
            if ch[0]==220:
                ch=smtpObj.login(WEB_EMAIL,PASSWORD)
                if ch[0]==235:
                    m_e=smtpObj.sendmail(
                        WEB_EMAIL,DEV_EMAIL,
                        'Subject: New User Sukuuhub\n'
                        'Name: {},\n\nph:{}'.format(
                            str(u),str(p)))   
        smtpObj.quit()   
    def mailq():
        if a_q._data:
            aq_list=a_q.get('active')
            s=db.collection('mailing').document('shs'+curr).collection(
            'questions').where('sj','==',curr).where(
                'q','in',aq_list).select(['q','n_u','n']).limit(5).stream()
            l=[]
            for doc in s:
                l.append(doc)
                            
            smtpObj = smtplib.SMTP('smtp.gmail.com', 587)
            ch=smtpObj.ehlo()
            if ch[0]==250:
                ch=smtpObj.starttls()
                if ch[0]==220:
                    ch=smtpObj.login(WEB_EMAIL,PASSWORD)
            sec='section_A'
            qn=None
            for doc in l:
                u=doc.get('n_u')
                n=doc.get('n')
                qn=doc.get('q')
                fpath=render_field_path([sec,str(qn)])
                q_d=db.collection('shs'+curr).document('2013').get([fpath])
                ovs=q_d.get(render_field_path([sec,str(qn),'o'])).split('_')
                footer="see question,answers and more at: https://www.sukuuhub.com\n\n"
                "Do not reply to this email"
                if ch[0]==235:
                    for i,ad in enumerate(u):
                        m_e=smtpObj.sendmail(
                        WEB_EMAIL,ad,
                        'Subject: Question of the day.\n'
                        'Dear {},\n{}\n{}\n\n{}\n\n{}'.format(
                            n[i],curr,q_d.get(render_field_path([sec,str(qn),'q'])),
                            '\n'.join(ovs),footer))
                        if m_e:
                            mail_errors.append(m_e)           
            
                if mail_errors:
                    db.collection('mailing').document('shs').collection(
                    'errors').document(curr).set({
                        str(qn)+dy:firestore.ArrayUnion(
                        mail_errors)},True)
                t_d=db.collection('mailing').document('shs'+curr).collection(
                    'questions').document('q_'+str(qn+1)).get(['q','space'])
                doc.reference.update({'n_u':firestore.ArrayRemove(u),
                                      'n':firestore.ArrayRemove(n)})
                data_s=getSize(u)+getSize(n)                
                if t_d.exists:
                    if 'space' in t_d._data:
                        spc=t_d.get('space')
                        if data_s < spc:
                            t_d.reference.update({'n_u':firestore.ArrayUnion(u),
                                          'n':firestore.ArrayUnion(n),
                                        'space':spc-data_s})
                        else:
                            t_d.reference.parent.document().set({'q':qn+1,
                                    'n_u':u,'sj':curr,'n':n,
                                        'space':1000000-data_s})
                    else:
                        t_d.reference.update({'n_u':firestore.ArrayUnion(u),
                                          'n':firestore.ArrayUnion(n)})
                else:
                    t_d.reference.set({'q':qn+1,
                                       'n_u':u,'sj':curr,'n':n,
                                       'space':1000000-data_s})
            
            if qn:
                if qn<20:
                    a_q.reference.update({'active':firestore.ArrayRemove([qn])})
                    a_q.reference.update({'active':firestore.ArrayUnion([qn+1])})
                else:
                    a_q.reference.update({'active':firestore.ArrayRemove([qn])})
            else:
                smtpObj.sendmail(
                        WEB_EMAIL,DEV_EMAIL,
                        'Subject: Error mail.\n  nothing was sent.\n\n'+err)
    
            smtpObj.quit()
    mailq()
    if mail_errors:
        return 'errors'
    else:
        return "ok"
                   
##    m_list
##    n=m_list.get('n')
##    q_d=db.collection('shs'+curr).document('2013').get()
##    for i in range(1,n+1):
##        user=m_list.get(render_field_path([i]))
##        if curr in user.sjs:
##            q_n=user.sjs.get(curr,None)+1
##        else:
##            q_n=1
