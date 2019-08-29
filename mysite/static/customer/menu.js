
$(document).ready(function(){

var toggler = document.getElementsByClassName("caret");
var i;
console.log('init\n toggler lenght is '+  toggler.length)
for (i = 0; i < toggler.length; i++) {
    console.log('listener '+i)
  toggler[i].addEventListener("click", function() {
    this.parentElement.querySelector(".nested").classList.toggle("active");
    this.classList.toggle("caret-down");
    console.log('click')
  });}


})