window.onload=function(){
    document.testUpdate.onsubmit=function(e){
    ques_data={};
    ques_data.q={};
    ques_data.num_q=0;
    $("form[name='testUpdate'] .question").each(function (){
    var data={};//op={};
    //ques_data[this.name.split("_")[1]]=data;
    ques_data.q[this.name]=data;
    //data.q=this.value; data.o=op;
    data.q=this.value;
    ques_data.num_q+=1;
    //$(this.className.split(' ')[0]+" .multichoice").each(function() {
    $(".multichoice.q"+this.name).each(function(i) {
    //op[this.name]=this.value;
    if (i>0) data.o +=('_'+this.value);
    else data.o = this.value;
    })})
    $("form[name='testmeta'] input").each(function() {
    if (this.type=="radio" && !(this.checked)) return;
    if (this.type=="date" && !(this.checked)) return;
    if (this.name=="date") {
      if (ques_data.nodate) return;
    } 
    if (this.disabled || this.type=="submit" || this.type=="button" || 
    this.type=="reset" ) return;

    ques_data[this.name]=this.value;})
    //ques_data.id=(new Date()).toISOString().split('T')[0];
    $.post({url:"/testupdate",
    data:JSON.stringify(ques_data),
    contentType:"application/json",
    success:respf,
    error:function(){ alert('error ocurred, please try again');}
  });
    return false;}
    document.testmeta.date.min=(new Date()).toISOString().split('T')[0];
    }

    function disableTime(){
        if (this.value=="duration" && this.checked) {
          $("input[name='stime'],input[name='etime']").each(function(){this.disabled=true})
          document.testmeta.duration.disabled=false;
        }
       else if (this.value=="schedule" && this.checked) {
         document.testmeta.duration.disabled=true;
         $("input[name='stime'],input[name='etime']").each(function(){this.disabled=false})
       }
      }