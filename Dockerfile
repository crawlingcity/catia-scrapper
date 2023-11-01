# Use the official lightweight Python image.
# https://hub.docker.com/_/python
FROM python:3.11.5-slim-bookworm

# Set the working directory
WORKDIR /usr/src/app

# Install gcc and other necessary packages
RUN apt-get update && \
    apt-get install -y gcc && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy the current directory contents into the container at /usr/src/app
COPY . /usr/src/app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 80 available to the world outside this container
EXPOSE 80

# Define environment variable
ENV NAME World

# Run app.py when the container launches
CMD ["gunicorn", "-b", "0.0.0.0:80", "app:app"]
