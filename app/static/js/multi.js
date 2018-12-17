$(document).ready(function(){
  console.log("entered popup")
  $("#multi").modal('show');

  var checkboxes = $("input[type='checkbox']"),
      submitButt = $("input[type='submit']");

  console.log("checkbox disabled")

  // document.getElementById("reschedule").disabled = true;

  document.getElementById("rescheduleMulti").onclick = function (e) {
  	//
      if (!CheckBoxCount()) {
          e.preventDefault();
      	// document.getElementById("reschedule").disabled = false;
          // document.forms[0].submit();
      };
  };

  function CheckBoxCount() {
      var inputList = document.getElementsByTagName("input");
      var numChecked = 0;

      for (var i = 0; i < inputList.length; i++) {
          if (inputList[i].type == "checkbox" && inputList[i].checked) {
              numChecked = numChecked + 1;
          }
      }
      if (numChecked < 1) {
          alert("Choose at least one event to reschedule !"); return false;
      }
      // alert("selected count: " + numChecked);

      return true;
  }

});
