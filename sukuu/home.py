from flask import (Blueprint,render_template,g,redirect,send_from_directory)
from sukuu.firestoreModels1 import db
from sukuu import settings
import datetime as dt
bp=Blueprint('home',__name__)
@bp.route('/ghana/wassce')
def index():
    c_r=db.collection('questionrecords')
    snap=c_r.document('records').get().to_dict()
    g.setdefault('menu',snap)
    snap1=c_r.document('latest').get().to_dict()
    u=['https://www.sukuuhub.com/static/']
    p=['wassce-exams.jpg','FB_boys_friends.jpg','FB_sen_girl.jpg',
       'FB_girls_friends.jpg','FB_students_lab.jpg','FB_boys_friends2.jpg',
       'presec.jpg','mean_girls.jpg','aburigirls_withflags.jpg',
       'girls_happy.jpg']
    u.append(p[int(str(dt.date.today().day)[-1])])
    g.fbim=u

    
    

    return render_template('index.html',menu=snap,latest=snap1)

#for local development and testing
if settings.SUKUU_LOCAL:
   @bp.route('/')
   def lhome():
      return redirect('/static/index.html')
   @bp.route('/js/<item>')
   def ljs(item):
      return redirect('/static/js/'+item)
   @bp.route('/css/<item>')
   def lcss(item):
      return redirect('/static/css/'+item)
   @bp.route('/fonts/<item>')
   def lfonts(item):
      return redirect('/static/fonts/'+item)
   @bp.route('/images/<item>')
   def limages(item):
      return redirect('/static/images/'+item)
   @bp.route('/contact')
   def lcontact():
      return redirect('/static/html/contact.html')
   @bp.route('/login')
   def llogin():
      return redirect('/static/html/login.html')
   @bp.route('/make/test')
   def lmaketest():
      return redirect('/static/html/makeTest.html')
   @bp.route('/file/<file>')
   def send_local_files(file):
      return send_from_directory(
         r"C:\Users\Public\Documents\free css\W3.CSS social media_files",
         filename=file)
