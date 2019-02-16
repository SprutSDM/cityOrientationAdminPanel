function getFileName(id) {
    var file = document.getElementById('uploaded-file-' + id).value;
    file = file.replace(/\\/g, '/').split('/').pop();
    document.getElementById('file-name-' + id).innerHTML = file;
}
function removeImgHolder(id) {
    var file = document.getElementById('img-holder-' + id).name = ''
}