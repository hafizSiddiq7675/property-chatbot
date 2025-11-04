# Use the official Rasa image as a base
FROM rasa/rasa:3.5.0

# Switch to the root user to install dependencies
USER root

# Copy the requirements file into the image
COPY requirements.txt requirements.txt

# Install Python dependencies
RUN pip install -r requirements.txt

# Switch back to the rasa user
USER rasa

# Copy the rest of the bot files into the image
COPY . .

# Train the Rasa model
# RUN rasa train

# Expose the port for the action server
EXPOSE 5055

# Command to run the action server
CMD ["rasa", "run", "actions"]
