
# Use a lightweight Python base image
FROM python:3.10.6

# Set working directory inside container
WORKDIR /app

# Install system dependencies required for builds
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy all project files into container
COPY . .

# Create outputs directory with secure permissions
RUN mkdir -p outputs && chmod 700 outputs

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Expose Flask's default port
EXPOSE 5000

# Run the app using Python
CMD ["python", "main.py"]


