# Property Investment Validation Chatbot

This is a Rasa-powered chatbot that helps users validate property investment data.

## Setup Instructions

### Local Setup (without Docker)

1.  Install the required Python packages:
    ```
    pip install -r requirements.txt
    ```
2.  Navigate to the project directory:
    ```
    cd property_chatbot
    ```
3.  Train the Rasa model:
    ```
    rasa train
    ```
4.  In one terminal, run the action server:
    ```
    rasa run actions
    ```
5.  In another terminal, run the chatbot shell:
    ```
    rasa shell
    ```

### Docker Setup

1.  Build and run the containers:
    ```
    docker-compose up --build
    ```
2.  The chatbot will be accessible through the container output.
3.  To stop the containers:
    ```
    docker-compose down
    ```

## Conversation Flow Example

```
USER: Hello
BOT: 👋 Welcome! Let's validate your property investment. What's the sales price?

USER: The property costs 250000
BOT: 🟢 GREEN - Sales Price is acceptable ($250,000). Next, what's your down payment?

USER: I have 50000 down
BOT: 🟢 GREEN - Optimal Down Payment - 20.0% down. Excellent equity position! Now, what's the interest rate?

USER: 7.5%
BOT: 🟢 GREEN - Optimal Interest Rate - 7.5% is competitive. 
     📊 Summary:
     - Sales Price: $250,000
     - Down Payment: $50,000 (20%)
     - Loan Amount: $200,000
     - Monthly Payment: ~$1,399
     Would you like to adjust anything or start over?

USER: Reset
BOT: 🔄 Starting fresh! and start with greeting "Hi".
```
