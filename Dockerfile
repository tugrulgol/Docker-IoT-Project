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

# Copy the Python script into the container
COPY iot_project.py /app/

# Run the script when the container starts
CMD ["python", "iot_project.py"]

