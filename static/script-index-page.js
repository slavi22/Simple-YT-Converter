function validateInputField(link){
    let pattern = /(?:https?:\/\/)?(?:www\.)?youtu\.?be(?:\.com)?\/?.*(?:watch|embed)?(?:.*v=|v\/|\/)([\w\-_]+)\&?/gm;
    if(!pattern.test(link)){
        return false
    }
    else{
        return true;
    }
}

document.addEventListener("DOMContentLoaded", function(){
    document.getElementById("btnSubmit").addEventListener("click", function(e){
        let videoLink = document.getElementById("inputVideoLink").value
        if(validateInputField(videoLink)==false){
            e.preventDefault()
            alert("Invalid link. Please enter a valid link!")
        }
    })
})