console.log("easing");
$("li:nth-child(1)").show("drop", 1000, function() {
$("li:nth-child(2)").delay(1000).show("drop", {direction: "down",easing: 'easeInOutExpo'},1000, function() {
$("li:nth-child(3)").delay(1000).show("drop", {direction: "down",easing: 'easeInOutCirc'},1000, function() {
$("li:nth-child(4)").delay(1000).show("drop", {direction: "down",easing: 'easeInOutCirc'},1000, function() {
$("li:nth-child(5)").delay(1000).show("drop", {direction: "down",easing: 'easeInOutCirc'},1000, function() {
}); 
});
}); 
});
}); 


// https://codepen.io/rockkk/pen/JKjMdJ






