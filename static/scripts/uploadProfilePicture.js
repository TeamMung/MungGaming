function uploadProfilePicture(image) {
    let formData = new FormData();
    formData.append("image", image);
    console.log(image);
    fetch("/images/profile/upload", {
        method: "POST",
        body: formData
    }).then(response => response.json()).then(data => {
        if (data.success) {
            document.getElementById("profilePicture").src += "?" + new Date().getTime();
        }
        else {
            alert(data.error);
        }
});
}

var input = document.getElementById("profilePictureInput");
input.addEventListener("change", function() {
    let image = input.files[0];
    uploadProfilePicture(image);
});
input.addEventListener("dragover", function(event) {
    event.preventDefault();
});
input.addEventListener("drop", function(event) {
    event.preventDefault();
    let image = event.dataTransfer.files[0];
    uploadProfilePicture(image);
});