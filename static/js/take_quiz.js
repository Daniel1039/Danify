
const cbtBtn = document.getElementById("cbt-calc-btn");
const cbtCalc = document.getElementById("cbt-calculator");
const cbtOverlay = document.getElementById("cbt-calc-overlay");
const cbtClose = document.getElementById("cbt-close-calc");
const cbtDisplay = document.getElementById("cbt-calc-display");


cbtBtn.onclick = () => {
    cbtCalc.style.display = "block";
    cbtOverlay.style.display = "block";
    setTimeout(()=>cbtCalc.classList.add("active"),10);
};


cbtClose.onclick = closeCbtCalc;
cbtOverlay.onclick = closeCbtCalc;


function closeCbtCalc(){
    cbtCalc.classList.remove("active");
    setTimeout(()=>{
        cbtCalc.style.display = "none";
        cbtOverlay.style.display = "none";
    },200);
}


function cbtAppend(val){
    cbtDisplay.value += val;
}


function cbtClear(){
    cbtDisplay.value = "";
}


function cbtBack(){
    cbtDisplay.value = cbtDisplay.value.slice(0,-1);
}


function cbtCalculate(){
    try{
        cbtDisplay.value = eval(cbtDisplay.value);
    }catch{
        cbtDisplay.value = "Error";
    }
}






