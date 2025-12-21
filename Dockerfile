# Use the official Python image
FROM python:3.10-slim

# Set the working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose the port used by Streamlit (Hugging Face uses 7860 by default)
EXPOSE 7860

# Run the application
CMD ["streamlit", "run", "app.py", "--server.address", "0.0.0.0", "--server.port", "7860"]