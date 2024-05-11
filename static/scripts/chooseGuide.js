// function init(){
//     gsap.registerPlugin(ScrollTrigger);

// // Using Locomotive Scroll from Locomotive https://github.com/locomotivemtl/locomotive-scroll

// const locoScroll = new LocomotiveScroll({
//   el: document.querySelector("#main"),
//   smooth: true
// });
// // each time Locomotive Scroll updates, tell ScrollTrigger to update too (sync positioning)
// locoScroll.on("scroll", ScrollTrigger.update);

// // tell ScrollTrigger to use these proxy methods for the "#main" element since Locomotive Scroll is hijacking things
// ScrollTrigger.scrollerProxy("#main", {
//   scrollTop(value) {
//     return arguments.length ? locoScroll.scrollTo(value, 0, 0) : locoScroll.scroll.instance.scroll.y;
//   }, // we don't have to define a scrollLeft because we're only scrolling vertically.
//   getBoundingClientRect() {
//     return {top: 0, left: 0, width: window.innerWidth, height: window.innerHeight};
//   },
//   // LocomotiveScroll handles things completely differently on mobile devices - it doesn't even transform the container at all! So to get the correct behavior and avoid jitters, we should pin things with position: fixed on mobile. We sense it by checking to see if there's a transform applied to the container (the LocomotiveScroll-controlled element).
//   pinType: document.querySelector("#main").style.transform ? "transform" : "fixed"
// });





// // each time the window updates, we should refresh ScrollTrigger and then update LocomotiveScroll.
// ScrollTrigger.addEventListener("refresh", () => locoScroll.update());

// // after everything is set up, refresh() ScrollTrigger and update LocomotiveScroll because padding may have been added for pinning, etc.
// ScrollTrigger.refresh();
// }
// init()

// Initialize Locomotive Scroll
const scroll = new LocomotiveScroll({
  el: document.querySelector('#main'),
  smooth: true
});
function disableScroll() {
  scroll.stop(); // This stops Locomotive Scroll from updating the scroll position
  document.body.style.overflow = 'hidden'; // This disables native scrolling of the body
}

// Function to enable scrolling
function enableScroll() {
  scroll.start(); // This resumes Locomotive Scroll
  document.body.style.overflow = ''; // This re-enables native scrolling of the body
}
$ = function(id) {
  return document.getElementById(id);

}

var show = function(id) {
	$(id).style.display ='block';
  disableScroll();
}
var hide = function(id) {
	$(id).style.display ='none';
  enableScroll();
  // closePopup()
}

// Function to disable scrolling


// Example code to open the pop-up
// const popup = document.getElementsByClassName('popup');

// function openPopup() {
//   popup.style.display = 'block';

//   disableScroll(); // Call disableScroll() when opening the pop-up
// }

// // Example code to close the pop-up
// function closePopup() {
//   popup.style.display = 'none';

//   enableScroll(); // Call enableScroll() when closing the pop-up
// }





// document.addEventListener('DOMContentLoaded', function() {
//   var popUpTrigger = document.getElementById('wrapper_img');
//   var popUp = document.getElementsByClassName('popup');

//   popUpTrigger.addEventListener('click', function(event) {
//       event.preventDefault();

//       popUp.style.display = 'block';
//   });
// });


/* when modal is closed */
// document.querySelector("#close").addEventListener('click', function() {
//   document.querySelector("#popup").style.display = 'none';
//   document.querySelector("body").style.overflow = 'visible';
//     var popUpTrigger = document.getElementById('wrapper_img');
//       popUpTrigger.addEventListener('click', function(event) {
//       event.preventDefault();
//         });

// });