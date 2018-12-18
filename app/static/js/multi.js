//Popup for multi-event scheduling appears and checks if any checkboxes
//are checked through CheckBoxCount() function. Then, returns True or False.
//From variety post of stack overflow, but specifcally Lalji Dhameliya:
//https://stackoverflow.com/questions/901712/how-to-check-whether-a-checkbox-is-checked-in-jquery 

$(document).ready(function(){
  $("#multi").modal('show');

  var checkboxes = $("input[type='checkbox']"),
      submitButt = $("input[type='submit']");

  document.getElementById("rescheduleMulti").onclick = function (e) {
      if (!CheckBoxCount()) {
          e.preventDefault();
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
      return true;
  }
});
