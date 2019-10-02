
$(document).ready(function(){

$("#action_select").change(function() {
  var action = $("#action_select").val();
  if (action === 'DELIV')
  {
    $("#deliv_date").show()
  }
  else
  {
    $("#deliv_date").hide()
  }

})
// $("#deliv_date").hide()
})

