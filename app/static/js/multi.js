var checkboxes = $("input[type='checkbox']"),
    submitButt = $("input[type='submit']");

console.log("checkbox disabled")

// document.getElementById("reschedule").disabled = true;

document.getElementsById("reschedule").onclick = function (e) {
	e.preventDefault();
    if (CheckBoxCount()) {
    	// document.getElementById("reschedule").disabled = false;
        document.forms[0].submit();
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
        alert("Minimum 1 !"); return false;
    } 
    alert("selected count: " + numChecked);

    return true;

}