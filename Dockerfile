# Use the official Python image from the Docker Hub
FROM python:3.9

# Set the working directory
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Upgrade pip and install system dependencies
RUN pip install --upgrade pip \
    && apt-get update \
    && apt-get install -y \
    libgpiod2 \
    libgpiod-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python packages from requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
#RUN pip install --upgrade influxdb-client

# Copy the Python scripts into the container
COPY sensor_app.py /app/
COPY mqtt_handler.py /app/ 

# Run the script when the container starts
CMD ["python", "sensor_app.py"]

