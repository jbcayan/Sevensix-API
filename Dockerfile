# Use a slim Python base image
FROM python:3.12-slim

# Set environment variables to minimize Python buffer issues
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Create a work directory for your application
WORKDIR /app

# Copy the requirements file first and install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your code into the container
COPY . /app

# Expose the port your app runs on (FastAPI default in your code is 8000)
EXPOSE 8000

# By default, run Uvicorn on startup
# Using "exec form" of ENTRYPOINT for signal handling in Docker
ENTRYPOINT ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]