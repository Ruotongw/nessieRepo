// display events on the calendar and add interactivity to bottoms

// Initializing variables
var month_names = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
var month_number = ["01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12"];
var day_name = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];
var year = parseInt($(".year").attr('id'));

// console.log("load event");

//
//If the add event button is clicked, create new event box
//
function add_event() {
	// Initializing new event box's input field as blank
	$("#eventName").val("");
	$("#eventDuration").val("");
	$("#eventDescription").val("");

	// Displaying new event box at apt location
	var windowWidth = $(window).width();
	var windowHeight = $(window).height();

	$("#addEvent").show().css({
		"position": "fixed",
		"width":"50%",
		"top":"40%",
		"left":"25%"
	});

function cancel_event(){
	$("#addEvent").hide();
}
}

function my_preferences(){
  // document.getElementById("preferences").style.display = "block";
	$("#earliestWorkTime").val("");
	$("#latestWorkTime").val("");

	// Displaying new event box at apt location
	var windowWidth = $(window).width();
	var windowHeight = $(window).height();

	$("#preferences").show().css({
		"position": "fixed",
		"width":"50%",
		"top":"40%",
		"left":"25%"
	});

	function cancel_event(){
		$("#preferences").hide();
	}
}

	// console.log(windowHeight);


//
// popup display
//
//appends an "active" class to .popup and .popup-content when the "Open" button is clicked
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

//
// Close new event box and edit event box and remove color from selected event
//
function closeEveBox(e) {
	e.preventDefault();

	$(".event-rectangles").removeClass("event-rectangle-select");
	$("#addEvent").hide();
}

//
// [NOT CURRENTLY USEING]Check if the event is all day event by checking the Font Awesome Icon state
//
function allDay() {
	if ($(".fa-check-square-o").length) {
		$("#eventStartDate, #eventStartTime, #eventEndDate, #eventEndTime").attr("disabled", false);
		$("#eventAllDay").removeClass("fa-check-square-o").addClass("fa-square-o");
	} else {
		$("#eventStartDate, #eventStartTime, #eventEndDate, #eventEndTime").attr("disabled", true);
		$("#eventAllDay").removeClass("fa-square-o").addClass("fa-check-square-o");
	}
}

//
// [NOT CURRENTLY USEING]Updating the clicked event
//
function updateEvent(e) {
	console.log('got into updateEvent');

	e.preventDefault();

	$("#error").text("");
	var eventId = $("#eventId").val();
	var eventName = $("#eventName").val();
	var eventLocation = $("#eventLocation").val();
	var eventStartDate = String($("#eventStartDate").val());
	var eventStartTime = String($("#eventStartTime").val());
	var eventEndDate = String($("#eventEndDate").val());
	var eventEndTime = String($("#eventEndTime").val());
	var eventDescription = $("#eventDescription").val();
	if ($(".fa-check-square-o").length) {
		var eventAllDay = 1;
		eventStartTime = "";
		eventEndTime = "";
	}
	else
		var eventAllDay = 0;

	if (eventStartDate > eventEndDate) {
		$("#error").text("End date cannot be earlier than start date");
	} else if (eventStartDate.substr(0, 7) != eventEndDate.substr(0, 7)) {
		$("#error").text("Event cannot stretch across months");
	} else if (eventStartTime != "" && eventEndTime == "") {
		$("#error").text("Fill both event start and end time");
	} else if (eventStartTime == "" && eventEndTime != "") {
		$("#error").text("Fill both event start and end time");
	} else {
		$.getJSON("updateEvent/", {eventId: eventId, eventName: eventName, eventLocation: eventLocation, eventStartDate: eventStartDate, eventStartTime: eventStartTime, eventEndDate: eventEndDate, eventEndTime: eventEndTime, eventAllDay: eventAllDay, eventDescription: eventDescription}, function(data) {
			// console.log(data);
			$("#status").text(data["result"]);
			$("#justForShowEvent").remove();
			$("#addEvent").hide();
			// refreshAllEvents();
		});
	}
}

//
// [NOT CURRENTLY USEING]Display clicked event's details when any event is clicked
//
function event_rectangle_clicked(event) {
	event.stopPropagation();
	console.log('stopPropogation passed');

	closeEveBox(event);
	console.log('got into event_rectangle_clicked');
	// console.log(event);
	$(".viewEveBoxName").text(event.target.innerHTML);
	var event_id = event.target.id;
	$("[id=" + event_id + "]").addClass("event-rectangle-select");
	$("#viewEveBoxEveId").text(event_id);
	// console.log(event);
	$.getJSON("viewEvent/", {eventId: event_id}, function(data) {
		// console.log(data);
		$(".viewTitle").text(data["event_name"]);
		$(".viewLocation").text(data["location"]);

		if (data["description"] != "") {
			$(".viewDescription").text(data["description"]);
		}

		var start_date = new Date(data["start_date"].replace(/-/g,'/'));
		var day_num = start_date.getDay();
		var day = day_name[day_num];
		var date = parseInt(data["start_date"].substr(8,2));
		var month = month_names[parseInt(data["start_date"].substr(5,2)) - 1];

		if (data["all_day"] == true || data["start_time"] == "") {
			$(".viewDay").text(day + ", " + month + " " + date);
		} else {
			$(".viewDay").text(data["start_time"] + ", " + day + ", " + month + " " + date);
		}

		var parent_td = $("#" + event.target.id).parent();
		// console.log(parent_td.width());
		var parent_td_left = parent_td.position().left;
		var parent_td_width = parent_td.width();
		var windowWidth = $(window).width();
		var eventBoxWidth = $("#viewEvent").width();
		if (parent_td_left + parent_td_width + eventBoxWidth + 30 > windowWidth) {
			$("#viewEvent").show().css({position:"absolute", top:(event.pageY - 120), left: (parent_td_left - eventBoxWidth)});
		} else {
			$("#viewEvent").show().css({position:"absolute", top:(event.pageY - 120), left: (parent_td_left + parent_td_width + 8)});
		}
	});
}

//
// [NOT CURRENTLY USEING]Delete an event
//
function deleteEve(event) {
	event.preventDefault();
	event.stopPropagation();

	var event_id = $("#viewEveBoxEveId").text();

	$.getJSON("deleteEvent/", {eventId: event_id}, function(data) {
		$("#status").text(data["result"]);
		closeEveBox(event);
		// refreshAllEvents();
	});
}

//
// [NOT CURRENTLY USEING]Display Edit event box with clicked event's details when an event is clicked
//
function editEve(event) {
	event.preventDefault();
	event.stopPropagation();

	var event_id = $("#viewEveBoxEveId").text();

	$.getJSON("viewEvent/", {eventId: event_id}, function(data) {
		$("#eventId").val(event_id);
		$("#eventName").val(data["event_name"]);
		$("#eventLocation").val(data["location"]);
		$("#eventStartDate").val(data["start_date"]);
		$("#eventStartTime").val(data["start_time"]);
		$("#eventEndDate").val(data["end_date"]);
		$("#eventEndTime").val(data["end_time"]);
		$("#eventDescription").val(data["description"]);
		if (data["all_day"] == true) {
			$("#eventStartDate, #eventStartTime, #eventEndDate, #eventEndTime").attr("disabled", true);
			$("#eventAllDay").removeClass("fa-square-o").addClass("fa-check-square-o");
		} else {
			$("#eventStartDate, #eventStartTime, #eventEndDate, #eventEndTime").attr("disabled", false);
			$("#eventAllDay").removeClass("fa-check-square-o").addClass("fa-square-o");
		}
		var date = parseInt(data["start_date"].substr(8,2));
		var month = month_names[parseInt(data["start_date"].substr(5,2)) - 1];
		$(".eveBoxDate").text(date + " " + month + " " + year);

		closeEveBox(event);
		$("#" + event_id).addClass("event-rectangle-select");
		if ($(window).width() > 750) {
			$("#addEvent").show().css({position: "absolute", top: (event.pageY - 375), left: (event.pageX - 220)});
		} else {
			$("#addEvent").show().css({position: "absolute", top: (event.pageY - 235), left: (event.pageX - 110)});
		}
	});
}

//
// Get events from the server and add each event to the calendar
//
function refreshAllEvents() {

	$(".event-rectangles").remove();

	$.get("allEvents", function(data) {
		console.log('test from js')
		console.log(data)
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
					eventDivId = parseInt(eventStartDate.substr(8, 2)) + month_names[month_number.indexOf(eventStartDate.substr(5, 2))];
					// console.log(eventDivId);
					// <a id=eventId  onclick='event_rectangle_clicked(event);' class='event event-rectangles d-block p-1 pl-2 pr-2 mb-1 rounded text-truncate small bg-info text-white'>eventId</a>
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
						eventDivId = parseInt(eventStartDate.substr(8, 2)) + j + month_names[month_number.indexOf(eventStartDate.substr(5, 2))];
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


// }
