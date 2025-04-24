// Add this to your existing JavaScript code
async function checkSymptoms(symptoms) {
    try {
        const response = await fetch('/api/check-symptoms', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ symptoms: symptoms })
        });
        const data = await response.json();
        
        if (data.success) {
            // Display symptoms analysis
            addMessage("Based on your symptoms, here's what I found:");
            data.data.forEach(symptom => {
                addMessage(`- ${symptom.name}: ${symptom.description}`);
            });
        } else {
            addMessage("I couldn't analyze your symptoms. Let's proceed with department selection.");
        }
    } catch (error) {
        console.error('Error checking symptoms:', error);
        addMessage("There was an error checking your symptoms. Let's proceed with department selection.");
    }
}

// Modify your window.onload function to include symptom checking
window.onload = async function() {
    addMessage("Welcome to MedCare! Would you like to describe your symptoms first?");
    addOptions(['Yes', 'No'], (response) => {
        if (response === 'Yes') {
            addMessage("Please describe your symptoms:");
            currentStep = 'symptoms';
        } else {
            proceedToDepartmentSelection();
        }
    });
}

// Add this function to handle symptom input
function handleSymptomInput(symptoms) {
    checkSymptoms(symptoms).then(() => {
        proceedToDepartmentSelection();
    });
}

// Update your sendMessage function to handle symptom input
function sendMessage() {
    const input = document.getElementById('userInput');
    const message = input.value.trim();
    
    if (message === '') return;
    
    addMessage(message, true);
    input.value = '';

    if (currentStep === 'symptoms') {
        handleSymptomInput(message);
    } else {
        // Your existing message handling code
    }
}