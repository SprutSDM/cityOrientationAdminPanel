function setRemove() {
    document.getElementById('save').value = 'remove';
}
function setAddTask(taskId) {
    document.getElementById('save').value = 'addTask';
    document.getElementById('task_id').value = taskId;
}
function setRemoveTask(taskId) {
    document.getElementById('save').value = 'removeTask';
    document.getElementById('task_id').value = taskId;
}