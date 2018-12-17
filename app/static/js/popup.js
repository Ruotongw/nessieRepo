

$(document).ready(function(){
  console.log("print running");
  $("#my-preferences").attr('disabled','disabled');
  $("#Signout").attr('disabled','disabled');
  $("#about").attr('disabled','disabled');
  $("#add-event").attr('disabled','disabled');
  console.log("disabled");
  $(".add-event").on("click", function(){
    $(".popup-overlay, .popup-content").addClass("active");
  });

  //removes the "active" class to .popup and .popup-content when the "Close" button is clicked
  $(".confirm, .popup-overlay").on("click", function(){
    $(".popup-overlay, .popup-content").removeClass("active");

  });

  $(".reschedule, .popup-overlay").on("click", function(){
    $(".popup-overlay, .popup-content").removeClass("active");
  });
  console.log("complete");
});
