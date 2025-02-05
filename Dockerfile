# Use an official Python runtime as a parent image.
FROM python:3.9-slim

# Set the working directory in the container.
WORKDIR /app

# Copy the requirements file and install Python dependencies.
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy the rest of the application code.
COPY . .

# Expose port 5000 for the Flask application.
EXPOSE 5000

# Set environment variable for Flask.
ENV FLASK_APP=app.py

# Run the application.
CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]
