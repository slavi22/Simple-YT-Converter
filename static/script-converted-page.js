document.addEventListener("DOMContentLoaded", function(){
    //document.getElementById("tableVideo").style.display = "none";
    //alert(document.getElementById("tableVideo").id)
    document.getElementById("btnVideo").addEventListener("click", function(){
        toggleTables(this.id);
    })
    document.getElementById("btnAudio").addEventListener("click", function(){
        toggleTables(this.id);
    })

})

function toggleTables(buttonId){
    let tableVideo = document.getElementById("tableVideo");
    let tableAudio = document.getElementById("tableAudio");
    if(buttonId == "btnVideo"){
        $("#btnAudio").removeClass(" activeButton");
        $("#btnVideo").addClass(" activeButton");
        $(`#${tableAudio.id}`).removeClass(" active").addClass(" nonActive");
        $(`#${tableVideo.id}`).addClass(" active").removeClass(" nonActive");
    }
    else{
        $("#btnVideo").removeClass(" activeButton");
        $("#btnAudio").addClass(" activeButton");
        $(`#${tableVideo.id}`).removeClass(" active").addClass(" nonActive");
        $(`#${tableAudio.id}`).addClass(" active").removeClass(" nonActive");
    }
}