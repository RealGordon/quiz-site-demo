var dispComments;
function dComments(e){
if (e) e.target.disabled="disabled";
localforage.getItem(blg).then(function(value) {
 
    if (value != null) {
	$('#comments-container').comments({
  getComments: function(success, error) {
	dispComments=success;
    success(value);},
	 postComment: postComf,
 upvoteComment: likef
  
});
} else getSerComments();
}).catch(function(err) { 
    console.log(err);
});
}
function getSerComments(){
$.getJSON('/confessions/comments/'+blg+'?q=confessions',function(r,s,x){
if (s == "success"){
$('#comments-container').comments({
  getComments: function(success, error) {
	dispComments=success;
    success(r);
  },
   postComment: postComf,
 upvoteComment: likef
});
localforage.setItem(blg, r).then(function (value) {
}).catch(function(err) {
    console.log(err);
});
}else error();
});
}

$('#comments-container').comments({
 postComment: postComf,
 upvoteComment: likef
});
function likef(commentJSON, success, error) {
 var c=blg;commentJSON.blg=blg;
 $.ajax({
 type:'POST',
 dataType:'json',
 url:'/confessions/comments/likes/'+blg+'?q=confessions',
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
 var checkcom;
 function postComf(commentJSON, success, error) {
 var c=blg;var v=[];commentJSON.blg=blg;
 var anon=document.getElementById("anon");
 if (anon.checked) commentJSON.anon=true;
 else { commentJSON.anon=false;
 if (!user){
 alert('you need to login before commenting else comment anonymously');
 window.location="/login/form?q="+window.location.pathname;
 }}
 //checkco=commentJSON;
     $.ajax({
	 type:'POST',
	 url:'/confessions/comments/'+blg+'?q=confessions', 
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
	 else {
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