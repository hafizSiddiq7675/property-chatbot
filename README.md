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

### Docker Setup (Recommended)

The project uses Docker Compose with 3 services: Rasa server, action server, and web interface.

#### Prerequisites
- Docker Desktop installed and running
- Docker Compose (included with Docker Desktop)

#### First Time Setup

Follow these steps in order for the initial setup:

1.  **Build the Docker images**:
    ```bash
    docker-compose build
    ```
    This builds the Docker images from the Dockerfile (does NOT train the model yet).

2.  **Train the Rasa model**:
    ```bash
    docker-compose run rasa train
    ```
    This creates a trained model and saves it to the `models/` directory on your local machine.
    The model persists via Docker volume, so you only need to do this once (or when training data changes).

3.  **Start all containers**:
    ```bash
    docker-compose up
    ```
    This will start:
    - Rasa server on `http://localhost:5005`
    - Action server on `http://localhost:5055`
    - Web interface on `http://localhost:8080`

4.  **Access the chatbot**:
    - Open your browser and navigate to `http://localhost:8080`
    - Or use the Rasa API at `http://localhost:5005`

#### Subsequent Runs

After the initial setup, you only need:

```bash
docker-compose up
```

The trained model persists in the `./models` directory, so you don't need to retrain unless you modify training data.

#### Stopping the Containers

```bash
docker-compose down
```

#### Useful Docker Commands

- **Retrain the model** (after updating training data in `data/` folder):
  ```bash
  # If containers are running:
  docker-compose exec rasa train

  # If containers are stopped:
  docker-compose run rasa train
  ```

- **Rebuild images** (after changing Dockerfile or requirements.txt):
  ```bash
  docker-compose build
  # Then restart containers:
  docker-compose up
  ```

- **Run in detached mode** (background):
  ```bash
  docker-compose up -d
  ```

- **View logs**:
  ```bash
  # All services
  docker-compose logs -f

  # Specific service
  docker-compose logs -f rasa
  docker-compose logs -f action_server
  ```

- **Restart a specific service**:
  ```bash
  docker-compose restart rasa
  docker-compose restart action_server
  ```

- **View container status**:
  ```bash
  docker-compose ps
  ```

- **Clean up everything** (remove containers, networks, volumes):
  ```bash
  docker-compose down -v
  ```

#### Understanding the Workflow

**Why train AFTER building?**
- Building the image is fast (installs dependencies only)
- Training happens separately and the model is saved to `./models/`
- You can retrain anytime without rebuilding the Docker image
- Best for development when training data changes frequently

**When to rebuild vs retrain:**
- **Rebuild** (`docker-compose build`): When you change `Dockerfile`, `requirements.txt`, or Python code
- **Retrain** (`docker-compose run rasa train`): When you change files in `data/`, `domain.yml`, or `actions/actions.py`

#### Configuration Notes
- Trained models are persisted in the `./models` directory via Docker volume
- Environment variable `BANK_RATE=6.5` is configured for the action server
- CORS is enabled to allow web interface communication
- The Dockerfile is based on `rasa/rasa:3.5.0` official image

## Conversation Flow Example

Here's a complete example of how the chatbot validates property investment data through an interactive conversation:

```
USER: Hello
BOT: 👋 Welcome! Let's do a quick property validation. What's the property zip code?

USER: 90210
BOT: ✅ Zip Code: 90210
     What state is the property in?

USER: California
BOT: ✅ State: CA
     What's the sales price?

USER: The property costs 350000
BOT: 🟢 GREEN - Sales Price is acceptable ($350,000).
     Is there a Lender's Title Insurance Policy? (Type 'yes' or 'no')

USER: yes
BOT: 🟢 GREEN - Lender's Title Insurance Policy: Yes (Good protection)
     What's the property type? Options:
     - sfh (Single Family Home)
     - condo
     - townhouse
     - multi-family (2-4 units)
     - mobile-home
     - raw-land

USER: sfh
BOT: 🟢 GREEN - Property Type: Single Family Home (Most marketable)
     Is this owner-occupied or non-owner-occupied? (Type 'owner' or 'non-owner')

USER: owner occupied
BOT: 🟢 GREEN - Owner-Occupied property (typically lower risk)
     What's your down payment amount?

USER: I have 70000 down
BOT: 🟢 GREEN - Optimal Down Payment - 20.0% down. Excellent equity position!
     What's the interest rate?

USER: 7.5%
BOT: 🟢 GREEN - Optimal Interest Rate - 7.50% is competitive.
     What's the loan term in years?

USER: 30 years
BOT: 🟢 GREEN - Loan Term: 30 years (standard term)

     📊 Property Investment Summary:

     📍 Location:
        • Zip Code: 90210
        • State: CA

     🏠 Property Details:
        • Property Type: Single Family Home
        • Occupancy: owner-occupied
        • Lender's Title Insurance: Yes

     💰 Financial Details:
        • Sales Price: $350,000
        • Down Payment: $70,000 (20.0%)
        • Loan Amount: $280,000
        • Interest Rate: 7.50%
        • Loan Term: 30 years
        • Monthly Payment: ~$1,958

     💡 Need a full detailed validation? Contact us for complete analysis.

     Type 'reset' to start a new calculation or 'hi' to begin again.

USER: Reset
BOT: 🔄 Starting fresh! and start with greeting "Hi".
```

### Validation Color Codes

The chatbot provides real-time feedback using color-coded indicators:

- 🟢 **GREEN** - Optimal/Acceptable value (meets best practices)
- 🟡 **YELLOW** - Warning or concern (requires attention)
- 🔴 **RED** - High risk (not recommended)

### Example Validation Scenarios

**Low Down Payment:**
```
USER: I have 15000 down (on $250,000 property = 6%)
BOT: 🟡 YELLOW - Minimum Down Payment - Target at least 10% (6.0% down).
```

**High Interest Rate:**
```
USER: 12%
BOT: 🟡 YELLOW - Usury Warning - High rate, consider refinancing (12.00%).
```

**Raw Land Property:**
```
USER: raw-land
BOT: 🔴 RED - Property Type: Raw Land (Higher risk - no improvements)
```
