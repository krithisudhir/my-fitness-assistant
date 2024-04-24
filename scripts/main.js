function processInput() {
    
    const userInput = document.getElementById('userInput').value;

    

    
    const response = mockNLPResponse(userInput);

    
    displayResponse(response);
}

function mockNLPResponse(input) {
    
    
    return `We will help you with "${input}". In the meantime, go to the gym!`;
}

function displayResponse(response) {
    
    const responseTextElement = document.getElementById('responseText');
    responseTextElement.textContent = response;
}
