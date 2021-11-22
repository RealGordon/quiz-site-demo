#import json
#import urllib.request
from google.cloud.firestore_v1.field_path import render_field_path
from google.cloud import firestore
import datetime as dt
from sukuu import settings
from werkzeug.security import generate_password_hash,check_password_hash
from flask import g
#import smtplib
def get_db():  
    if settings.SUKUU_LOCAL:
        db=firestore.Client.from_service_account_json(settings.JSON_CREDENTIALS)
        if settings.LOCAL_CLOUD_RESOURCES:
            import grpc
            from google.cloud.firestore_v1.gapic import firestore_client
            from google.cloud.firestore_v1.gapic.transports import firestore_grpc_transport
            channel = grpc.insecure_channel("localhost:8080")
            transport = firestore_grpc_transport.FirestoreGrpcTransport(channel=channel)
            db._firestore_api_internal = firestore_client.FirestoreClient(transport=transport)
    else:
        db=firestore.Client()
    return db
db=get_db()
class User:
    #getFacebookUser=getUser
    #old_user_status=check_user_status
    labels=['nick','name','phone','email','birthdate','school']
    def __init__(self,data=None,doc=None):
        self.doc_ref=None
        self.errors={}
        self.user_id=None
        if doc:
            self.doc_ref=doc.reference
            self.user_id=doc.id
            self.__dict__.update(doc.to_dict())
            self.__dict__.pop('pwd',None)
        else:
            s=db.collection('users').where('email','==',data['email']).stream()
            for doc in s:
                if doc.exists:
                    g.errors['account']='Account already exits'
                    return None
            else:
                data.setdefault('email','')
                data.setdefault('phone','')
                for k in ['pwd','birthdate','pwd-repeat','formtype']:
                    if k=='pwd':
                        data[k]=generate_password_hash(data.get(k))
                    elif k=='birthdate':
                        data[k]=dt.date.fromisoformat(data.get(k)).toordinal()
                    else:
                        data.pop(k,None)
                data.update({'dj':dt.date.today().isoformat()})
                self.doc_ref=db.collection('users').add(data)[1]
                self.user_id=self.doc_ref.id
                self.updateUserSex(data['sex'])                      
                db.collection('users').document('new_users').set({
                    'u':firestore.ArrayUnion([data['email']]),
                    'n':firestore.ArrayUnion([data['name']]),
                    'p':firestore.ArrayUnion([data['phone']])},True)

    @staticmethod       
    def updateUserSex(sex="M",m=None):
        if not m:
            m='site'
            doc_ref=db.collection('statistics').document(m)
            if sex=="M" or sex=="F":
                doc_ref.update({render_field_path([
                'users',str(dt.date.today().year),sex]):firestore.Increment(1)})
                 
    def save_new_user(self):
        if not self.old_user_status():
            self.doc_ref=db.collection('users').add(
                {"name":self.name,"email":self.email,
                 'access_token':self.access_token,'user_id':self.user_id
                 ,'date_registered':dt.date.today().toordinal(),
                 'login_method':'facebook'})[1]
            db.collection('statistics').document('facebook').update({
                'users':firestore.Increment(1)})
            
    
    def save_user_marks(self,subject,year,sec,n_q,n_mark):
        """   (subject,section,new question,new marks)"""
        year=str(year)
        doc_snap=self.doc_ref.get([render_field_path([subject,year])])
        ques_solved=doc_snap.get(render_field_path([subject,year,sec,'q']))
        user_mark=doc_snap.get(render_field_path([subject,year,sec,'marks']))
        ques_solved.append(n_q)
        user_mark+=int(n_mark)                        
        self.doc_ref.update({subject:{year:{sec:{'q':ques_solved,'marks':user_mark}}}})
        return {'marks':user_mark,'total_solved':len(ques_solved)}
        
    def save_answer(self,test_id,n_a,num):
        """            (str,dict,int)
        (test_id,new answers,num of questions)"""
        answers_snap=self.doc_ref.get([
            render_field_path([test_id,'answers'])])
        try:
            answers=answers_snap.get(
                render_field_path([test_id,'answers']))            
        except KeyError:
            answers=[0 for x in range(num)]
        for k,v in n_a.items():
            if v:
                answers[int(k)]=v
        self.doc_ref.update(
            {render_field_path([test_id,'answers']):answers})
    @classmethod
    def getdbUser(cls,g,*,user_id=None,email='',pwd='',e=True):
        """   user_id ,email , pwd , e=True)
        get a user from db"""
        labels=cls.labels[:]
        if user_id:
            d=db.collection('users').document(user_id).get(labels)
            if not d.exists:
                s=db.collection('users').where('user_id','==',user_id).select(
                    labels).limit(1).stream()
                for d in s:
                    return cls(doc=d)
                else:
                    return None
            return cls(doc=d)                      
        else:
            labels.append('pwd')
            if e:
                s=db.collection("users").where('email','==',email).select(
                    labels).stream()
            else:
                s=db.collection("users").where('phone','==',email).select(
                    labels).stream()
            for doc in s:
                if doc.exists:
                    if check_password_hash(doc.get('pwd'),pwd):
                        return cls(doc=doc)
                    else:
                        g.errors.update(account='An error occured, try again')
                        return False
                    
            else:
                g.errors.update(account='account does not exist')
        return False     
        
    def getAnswers(self,subject,year,sec='section_A'):
        num_q=self.sub_ref.get([render_field_path(['num_q'])]).get(
                render_field_path(['num_q']))
        try:
            answers=self.doc_ref.get(
                [render_field_path([subject,year,sec,'answers'])]).get(
                    render_field_path([subject,year,sec,'answers']))
            return answers
        except KeyError:
            return [0 for x in range(num_q)]
    def subref(self,s):
        """ (document_path(str))  """
        self.sub_ref=db.document(s)
        
        


    
