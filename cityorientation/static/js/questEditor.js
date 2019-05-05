function setRemove() {
    var file = document.getElementById('save').value = 'remove';
};
function replaceImg(input) {
    if (input.files && input.files[0]) {
        var reader = new FileReader();

        reader.onload = function(e) {
            document.getElementById('img-preview').style.background = 'url("' + e.target.result + '") center / cover';
        }

        reader.readAsDataURL(input.files[0]);
    }
};
$("#input-file").change(function() {
    replaceImg(this);
});