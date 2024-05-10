function init(){
    gsap.registerPlugin(ScrollTrigger);

// Using Locomotive Scroll from Locomotive https://github.com/locomotivemtl/locomotive-scroll

const locoScroll = new LocomotiveScroll({
  el: document.querySelector("#main"),
  smooth: true,
  multiplier:.7
});
// each time Locomotive Scroll updates, tell ScrollTrigger to update too (sync positioning)
locoScroll.on("scroll", ScrollTrigger.update);

// tell ScrollTrigger to use these proxy methods for the "#main" element since Locomotive Scroll is hijacking things
ScrollTrigger.scrollerProxy("#main", {
  scrollTop(value) {
    return arguments.length ? locoScroll.scrollTo(value, 0, 0) : locoScroll.scroll.instance.scroll.y;
  }, // we don't have to define a scrollLeft because we're only scrolling vertically.
  getBoundingClientRect() {
    return {top: 0, left: 0, width: window.innerWidth, height: window.innerHeight};
  },
  // LocomotiveScroll handles things completely differently on mobile devices - it doesn't even transform the container at all! So to get the correct behavior and avoid jitters, we should pin things with position: fixed on mobile. We sense it by checking to see if there's a transform applied to the container (the LocomotiveScroll-controlled element).
  pinType: document.querySelector("#main").style.transform ? "transform" : "fixed"
});





// each time the window updates, we should refresh ScrollTrigger and then update LocomotiveScroll.
ScrollTrigger.addEventListener("refresh", () => locoScroll.update());

// after everything is set up, refresh() ScrollTrigger and update LocomotiveScroll because padding may have been added for pinning, etc.
ScrollTrigger.refresh();
}
init()

function page2()
{
    var tl = gsap.timeline({
        scrollTrigger: {
            trigger: "#page2",
            start: "top top",
            scrub: 2,
            pin: true,
            scroller:"#main"
        }
      })
      .to("#circle",{
        rotate:0,
        ease:Expo.easeInOut,
        duration:2
    })


  var active=3
var mncircles=document.querySelectorAll(".mncircle");
var second=document.querySelectorAll(".second")
var abc=document.querySelector("#abc")

gsap.to(mncircles[active+1],{
    opacity:0.9
})
gsap.to(second[active+1],{
    opacity:1
})
mncircles.forEach(function(val,index){
    val.addEventListener("click",function(){
        gsap.to("#circle",{
            rotate:(3-(index+1))*10,
            ease:Expo.easeInOut,
            duration:1
        })

        greyout();
        gsap.to(this,{
            opacity:.5
        })

        gsap.to(second[index],{
            opacity:1

        })
    })
})
document.getElementById("mn1").addEventListener("click", myFunction);
function greyout()
{
    gsap.to(mncircles,{
        opacity:.2
    })
    gsap.to(second,{
        opacity:.4
    })
}

}

page2()

var circle = document.querySelector("#circl");
var centre = document.querySelector("#tags");
var nav = document.querySelector("#nav>h1");
window.addEventListener("mousemove",function(dets){
  gsap.to(circle, {
          x:dets.clientX,
          y:dets.clientY
  })

})