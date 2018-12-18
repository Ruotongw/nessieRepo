// display events on the calendar and add interactivity to buttons

// Initializing variables
var month_names = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
var month_number = ["01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12"];
var day_name = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];
var year = parseInt($(".year").attr('id'));
var month = parseInt($(".month").attr('id'));



//The below method restricts users from entering an assignment due in the past.
//This function is by Wajid khan from https://stackoverflow.com/questions/43274559/how-do-i-restrict-past-dates-in-html5-input-type-date
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

function add_event() {
	// Initializing new event box's input field as blank
	// var today = Date().toISOString().substr(0, 10);
	// $('#startPop').hide();
	$('#startPop').modal('hide');
	$("#dueDate").attr("min", new Date().toDateInputValue());
	console.log("open event form")

	// Displaying new event box at apt location
	var windowWidth = $(window).width();
	var windowHeight = $(window).height();

	$("#addEvent").modal('show');
}

function repChecked(){
	if($("#rep-checkbox").is(':checked')){
		console.log("checked");
	}  // checked
	else {
		console.log("setting value")
	    // unchecked
	    $("#eventRepetition").val("1");}
}

function close_event(){
	console.log("close")
	$('#addEventForm')[0].reset();
}

//
// Get events from the server and add each event to the calendar
//
function refreshAllEvents(month, year) {

	$(".event-rectangles").remove();

	$.get("allEvents", { "year": year, "month":month}, function(data) {
		console.log('test from js')
		// console.log(year)
		// console.log(data)
		// var event_id_end_date = data.split(" ");
		var event_list = [];
		for (var i = 0; i < data.length; i++) {
			event_list.push({event_id: data[i].summary, end_time: data[i].end.dateTime, start_time:data[i].start.dateTime});
		}

		// console.log(event_list)
		// console.log(event_list[13])

		for (var i = 0; i < event_list.length; i++) {
			try {
				var eventStartDate = event_list[i].start_time.substring(0, 10);
				// console.log(eventStartDate);
				var eventEndDate = event_list[i].end_time.substr(0, 10);
				var eventId = event_list[i].event_id;

				if (eventStartDate == eventEndDate) {
					eventDivId = parseInt(eventStartDate.substr(8, 2)) + month_names[month_number.indexOf(eventStartDate.substr(5, 2))]+ parseInt(eventStartDate.substr(0,4));
					// console.log(parseInt(eventStartDate.substr(0,4)));
					// <a id=eventId  onclick='event_rectangle_clicked(event);' class='event event-rectangles d-block p-1 pl-2 pr-2 mb-1 rounded text-truncate small bg-info text-white'>eventId</a>
					// console.log(eventId)
					// console.log(eventDivId)
					$("#" + eventDivId).append("<a id= "+eventId+" onclick='event_rectangle_clicked(event);' class='event event-rectangles d-block p-1 pl-2 pr-2 mb-1 rounded text-truncate small bg-info text-white'>"+eventId+"</a>");
				} else {
					var Date1 = eventStartDate;
					var Date2 = eventEndDate;
					Date1 = new Date(Date1.replace(/-/g,'/'));
					Date2 = new Date(Date2.replace(/-/g,'/'));
					var timeDiff = Math.abs(Date2.getTime() - Date1.getTime());
					var diffDays = Math.ceil(timeDiff / (1000 * 3600 * 24));
					// console.log(diffDays);

					for (var j = 0; j <= diffDays; j++) {
						eventDivId = parseInt(eventStartDate.substr(8, 2)) + j + month_names[month_number.indexOf(eventStartDate.substr(5, 2))+ eventStartDate.substr(0,4)];
						// console.log(eventDivId);
						$("#" + eventDivId).append("<a id= "+eventId+" onclick='event_rectangle_clicked(event);' class='event event-rectangles d-block p-1 pl-2 pr-2 mb-1 rounded text-truncate small bg-info text-white'>"+eventId+"</a>");
						// $("#" + eventDivId).append("<div onclick='event_rectangle_clicked(event);' class='event-rectangles joint-event' id='" + eventId +"'>Event " + (i + 1) + "</div>");
					}
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
