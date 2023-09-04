# Use the official lightweight Python image.
# https://hub.docker.com/_/python
FROM python:3.11.5-slim-bookworm

# Set the working directory
WORKDIR /usr/src/app

# Copy the requirements file into the container
COPY requirements.txt .

# Install production dependencies.
RUN pip install --no-cache-dir -r requirements.txt

# Copy local code to the container image.
COPY . .

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Run the web service on container startup.
CMD [ "gunicorn", "-w", "4", "app:app", "-b", "0.0.0.0:5000" ]
