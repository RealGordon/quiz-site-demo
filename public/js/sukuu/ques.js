function qdisplay(){
if (!qlength){
qltoint();
if (!qcount)qcount=Number(qlength[0]);
}
var count=false;
var check=false;
var check2=false;
var odata=qdata;



if (qcount>qmax){
check=true;
for (var i in fdata){
if (fdata[i][qcount]){
count=true;
qdata=fdata[i];
break;}
}
}
if (qcount<qmin){
check=true;
for (var i in fdata){
 if (fdata[i][qcount]){
 count=true;
 qdata=fdata[i];
 break;
}
}
}
if (check){
for (var i in fdata){
if (fdata[i][mqcount]){
check2=true;
break;}
}
}


if (check && !check2)fdata.push(odata);
if (check && count)qltoint();
if (check && !count) getQ();
else present();
}
function present(){
eltq.innerHTML="",elta.innerHTML="";
if ((Object.keys(qdata)).length!=0){
if (!qdata[qcount]){
if (Number(qcount) > Number(qlength[qlength.length-1]))qcount=qlength[0];}
eltq.innerHTML=String(qcount)+". "+qdata[qcount]['q'];
var ovs=qdata[qcount]['o'].split('_');
for (var i in ovs){
var ov=document.createElement('li');
var qa=document.createElement('input');
qa.type='radio';
qa.name="answer";
qa.value=qOps[i];
var qal=document.createElement('label');
qal.innerHTML=ovs[i];
ov.appendChild(qa);
ov.appendChild(qal);
elta.appendChild(ov);

}
var sU,sA;sA=$('#shared');sU=$('#sharedUser');
if (qdata[qcount].a){
sA.text('Answer '+qdata[qcount].a.o);
if (qdata[qcount].a.u) {sU.text(qdata[qcount].a.u[0]);
sU.css('display','block');
sU.attr('href','/profiles/'+qdata[qcount].a.u[1]);}
} else { sA.text('share answer');sU.css('display','hidden');}
$("#passa input").each(sAns);
$("#quesNav button").attr('disabled',false);
}else {
eltq.innerHTML="no more questions available";
$("#quesNav button").each(function(i,el){if (i==0)this.disabled=false;});
}
}
function getQ(){
$.getJSON('getquestions/shs/'+qsubject+'/'+qyear+'/?q='+qcount,function(r,st,x){
qdata=r;
qltoint();
present();
});
}
function sAns(i,el){
if (myans[qcount]){
if (this.value==myans[qcount]) {
this.checked="checked";
return false;
}
}
}
 function nextSlide(action,event){
$("#quesNav button").attr('disabled','disabled');
$('#passa input').each(aformSubmit);
$('#sharedUser').text('View Answer');
mqcount=qcount;
if (!qlength) qltoint();
qcount=Number(qcount);
if (qcount == Qmax){ 
if (action)qcount=qlength[0];
else qcount-=1;
}else if (qcount ==1){
if (action)qcount+=1;
}else{
if (action)qcount+=1;
else qcount-=1;}
qdisplay();
$("#correctAnswer").attr('disabled',false).text('View Answer');
$("#v-comm")[0].disabled=false;
$('#answerArea')[0].innerHTML="";
$('#comments-container')[0].innerHTML="";
$('#commContainer span')[0].innerHTML="";
if (f1){if (f1.parentNode)f1.parentNode.removeChild(f1);}
};


function aformSubmit(i,el){
if (this.checked){
if (myans[qcount]!= this.value){
submitAns[qcount]=this.value;
myans[qcount]=this.value;}
if ((Object.keys(submitAns)).length>=10){
var x=new XMLHttpRequest();
x.open('POST','getquestions/shs/'+qsubject+'/'+qyear);
x.setRequestHeader("Content-Type", "application/json");
x.onreadystatechange=function(){
if((x.readyState===XMLHttpRequest.Done||4) && (x.status===200)){
submitAns={};
};
}
x.send(JSON.stringify(submitAns));}
return false;}

}
function qltoint(){
qlength=Object.keys(qdata);
var t=new Array();
for (var i in qlength) t.push(Number(qlength[i]));
qlength=t;
qmin=qlength[0];
qmax=qlength[qlength.length-1];
}

var f1;
function sComments(e){
var f=e.target;
this.send.disabled="disabled";
con=this.udata.value;
$.ajax({
type:'POST',url:'/education/comments/',
contentType:'application/json',
data:JSON.stringify({'content':con,user_has_upvoted:false,upvote_count:0,
'id':1,'q':qcount,'parent':null}),
success:function(r,s,x){
if (s=="success"){
//$('#ucomments')[0].appendChild(x.responseXML);
f.udata.value="";
f.send.disabled=false;
f1.parentNode.removeChild(f1);
dComments(null);
}
}
});
return false;
}
function createComment(){
var a,p1,p2,ta,b,h,c,d=document;
fm=d.createElement('form');
h=d.createElement('span');
c=d.createElement('input');
p1=d.createElement('p');
p2=d.createElement('div');
ta=d.createElement('textarea');
h.textContent="Reply ";h.className="w3-btn";h.id="rlabel";
b=d.createElement('input');b.type="submit";c.type="reset";
fm.className="w3-panel w3-card-4";
ta.placeholder="write solution or comment here";ta.name="udata";ta.required="required";
ta.className="w3-input";
c.className="w3-btn w3-orange w3-bar-item";p2.className="w3-bar";
b.className="w3-btn w3-blue w3-bar-item";
p1.appendChild(ta);p2.appendChild(c);
p2.appendChild(b);
a=[h,p1,p2];
for (var i in a) fm.appendChild(a[i]);
fm.onsubmit=sComments;
$('#commContainer')[0].appendChild(fm);
b.id="send";
f1=fm;
}



function correctAnswer(e){
var t,sU;t=e.target;sU=$('#answerArea');
var n=t.nextSibling;
t.disabled="disabled";
if (qdata[qcount].a){
sU.css('display','block');
if (qdata[qcount].a.u){ sU.html(qdata[qcount].a.a);
var l=document.createElement('a');
l.href='/profiles/'+qdata[qcount].a.u[1];
l.className="w3-bar-item w3-btn";l.textContent=qdata[qcount].a.u[0];
t.parentNode.appendChild(l);
}else {
n.textContent="Provided by Sukuuhub Team";
sU.html(qdata[qcount].a.a);}
}else {
n.textContent="no answer available";
sU.css('display','hidden');
}
}

function dComments(e){
if (e) e.target.disabled="disabled";
else $('#commContainer button')[0].disabled='disabled';
localforage.getItem(qsubject+'_'+qyear+'_'+qcount).then(function(value) {
 
    if (value != null) {
	$('#comments-container').comments({
  getComments: function(success, error) {
	dispComments=success;
    success(value);getSerComments();},
	 postComment: postComf,
 upvoteComment: likef
  
});
}
	else getSerComments();
}).catch(function(err) { 
    console.log(err);
});
function getSerComments(){
$.getJSON('/education/comments/?q='+qcount,function(r,s,x){
if (s == "success"){
if (r[0] != 'no comments' ){
$('#comments-container').comments({
  getComments: function(success, error) {
	dispComments=success;
    success(r);
  },
   postComment: postComf,
 upvoteComment: likef
});
localforage.setItem(qsubject+'_'+qyear+'_'+qcount, r).then(function (value) {
}).catch(function(err) {
    console.log(err);
});

} else { 
$('#comments-container').comments({
  getComments: function(success, error) {
	dispComments=success;
    success([]);
  },
   postComment: postComf,
 upvoteComment: likef
});
}
}

});}

}

$('#comments-container').comments({

 postComment: postComf,
 upvoteComment: likef
});
function likef(commentJSON, success, error) {
 commentJSON.q=qcount;
 var c=qsubject+'_'+qyear+'_'+qcount;
 $.ajax({
 type:'POST',
 url:'/education/comments/likes',
 data:JSON.stringify(commentJSON),
 contentType:'application/json',
 timeout:5000,
 success:function(r){
 success(commentJSON);
localforage.getItem(c).then(function(v) {
var p=parseInt(commentJSON.id);
v[p-1]=commentJSON;
localforage.setItem(c, v).then(function (value) {
}).catch(function(err) {
    console.log(err);
});
}).catch(function(err) {
   
    console.log(err);
});
},
 error:error
 });
 }
 
 function postComf(commentJSON, success, error) {
 var c=qsubject+'_'+qyear+'_'+qcount;
 var v=[];
	commentJSON.q=qcount;
     $.ajax({
	 type:'POST',
	 url:'/education/comments/', 
	 data:JSON.stringify(commentJSON),
	 dataType:'json',
	 contentType: 'application/json',
     success:function(r) {
	 localforage.getItem(c).then(function(va) {
	 if (va!= null)v=va;
	 if (r.length>1) {for (var i in r)
	 {r[i].is_new=true;
	 success(r[i]);
	 delete r[i].is_new;}
	 v.concat(r);
	 }
	 else {delete commentJSON['q'];
	 v.push(commentJSON);
	 success(commentJSON);
	 }
if (v.length>0) localforage.setItem(c, v).then(function (value) {
}).catch(function(err) {
    console.log(err);
});
}).catch(function(err) {
    console.log(err);
});
	 },
	timeout:8000,
	 error:error
    });}