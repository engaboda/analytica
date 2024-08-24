FROM python:3.10.12-slim

# Set the working directory within the container
WORKDIR .

# Copy the necessary files and directories into the container
COPY ./src ./src

COPY ./requirements.txt ./requirements.txt

# Upgrade pip and install Python dependencies
RUN pip install -r requirements.txt

# Expose port 5000 for the Flask application
EXPOSE 5000

# Define the command to run the Flask application using Gunicorn
CMD ["gunicorn", "--timeout", "20", "src.app:app", "-b", "0.0.0.0:5000", "-w", "4"]