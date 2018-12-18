// display events on the calendar and add interactivity to buttons

// Initialize variables
var month_names = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
var month_number = ["01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12"];
var day_name = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];
var year = parseInt($(".year").attr('id'));
var month = parseInt($(".month").attr('id'));

//
// Restricts users from entering an assignment due in the past.
//
Date.prototype.toDateInputValue = (function() {
  var local = new Date(this);
  local.setMinutes(this.getMinutes() - this.getTimezoneOffset());
  local.setDate(local.getDate()+1)
  console.log(local.getDate())
  return local.toJSON().slice(0,10);
});

$(document).ready(function(){
  $("#dueDate").attr("min", new Date().toDateInputValue());
});

//
// for add event button on the start page navigation form 
//
function add_event() {
	// hide start navigation form 
	$('#startPop').modal('hide');
	
	// show add event form 
	$("#addEvent").modal('show');
}

//
// for the checkbox in add event form: reset to one is unchecked
//
function repChecked(){
	if($("#rep-checkbox").is(':checked')){
		// console.log("checked");
	}  // checked
	else {
		// console.log("setting value")
	    // unchecked
	    $("#eventRepetition").val("1");
	}
}

//
// for the cancel button in add event form: reset all fields 
//
function close_event(){
	// console.log("close")
	$('#addEventForm')[0].reset();
	$("#eventRepetition").val("1");
}

//
// Get events from the server and add each event to the calendar
//
function refreshAllEvents(month, year) {

	$.get("allEvents", { "year": year, "month":month}, function(data) {
		
		// create a event list 
		var event_list = [];
		for (var i = 0; i < data.length; i++) {
			event_list.push({event_id: data[i].summary, end_time: data[i].end.dateTime, start_time:data[i].start.dateTime});
		}

		// append event to each day on the calendar
		for (var i = 0; i < event_list.length; i++) {
			try {
				var eventStartDate = event_list[i].start_time.substring(0, 10);
				var eventEndDate = event_list[i].end_time.substr(0, 10);
				var eventId = event_list[i].event_id;

				if (eventStartDate == eventEndDate) {
					eventDivId = parseInt(eventStartDate.substr(8, 2)) + month_names[month_number.indexOf(eventStartDate.substr(5, 2))]+ parseInt(eventStartDate.substr(0,4));
					$("#" + eventDivId).append("<a id= "+eventId+" onclick='event_rectangle_clicked(event);' class='event event-rectangles d-block p-1 pl-2 pr-2 mb-1 rounded text-truncate small bg-info text-white'>"+eventId+"</a>");
				} 
			}
			catch(error) {
			  console.error(error);
			  // expected output: SyntaxError: unterminated string literal
			  // Note - error messages will vary depending on browser
			}

		}
	});
}
