// chat/static/chat/js/chat.js
// Optional: scroll chat to bottom automatically
window.onload = function() {
    var chatBox = document.getElementById('chat-box');
    if(chatBox) chatBox.scrollTop = chatBox.scrollHeight;
};
