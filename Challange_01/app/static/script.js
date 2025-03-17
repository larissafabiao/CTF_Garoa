document.addEventListener('DOMContentLoaded', () => {
    const userInput = document.getElementById('user-input');
    const sendButton = document.getElementById('send-button');
    const messages = document.getElementById('chat-messages');

    const appendMessage = (message, sender) => {
        const messageDiv = document.createElement('div');
        messageDiv.textContent = `${sender}: ${message}`;
        messageDiv.classList.add('message', sender === 'User' ? 'user' : 'ai');
        messages.appendChild(messageDiv);
    };

    const sendMessage = async () => {
        const message = userInput.value.trim();
        if (!message) return;

        appendMessage(message, 'User');
        userInput.value = '';

        try {
            const response = await fetch('/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message }),
            });

            const data = await response.json();

            if (response.error) {
                appendMessage(data.error, 'System');
            } else {
                appendMessage(data.response, 'AI');
            }
        } catch (error) {
            console.error('Error:', error);
            appendMessage('Failed to communicate with the server.', 'System');
        }
    };

    sendButton.addEventListener('click', sendMessage);
});
