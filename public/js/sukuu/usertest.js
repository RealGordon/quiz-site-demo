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
var q_nums=Object.keys(qdata);
if (q_nums.length!=0){
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
//$.getJSON('getquestions/shs/'+qsubject+'/'+qyear+'/?q='+qcount,function(r,st,x){
$.getJSON('/test/getquestions/'+test_id+'?q='+qcount,function(r,st,x){
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
//x.open('POST','getquestions/shs/'+qsubject+'/'+qyear);
x.open('POST','/test/answers/'+test_id);
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

