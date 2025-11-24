




function loadmessage(author, message) {
    const chatbox = document.querySelector(".chat");

    if (author == 'user') {
        let messageUserBox = document.createElement('div');
        messageUserBox.className = 'box-message-user';

        let messageUser = document.createElement('div');
        messageUser.className = 'message-user';
        messageUser.innerHTML = message;

        messageUserBox.appendChild(messageUser);
        chatbox.appendChild(messageUserBox);
    } else {
        let messageIABox = document.createElement('div');
        messageIABox.className = 'box-message-ia';

        let messageIA = document.createElement('div');
        messageIA.className = 'message-ia';
        messageIA.innerHTML = message;

        messageIABox.appendChild(messageIA);
        chatbox.appendChild(messageIABox);
    }
    chatbox.scrolltop = chatbox.scrollHeight;
}
