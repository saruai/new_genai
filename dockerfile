FROM python:3.12-slim
LABEL maintainer="saru"

ENV PYTHONUNBUFFERED=1

# Set the working directory
WORKDIR /gen_AI

# Expose the necessary port
EXPOSE 8501

# Copy the requirements file
COPY requirements.txt .

# Install necessary system packages
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    python3-dev \
    libopenblas-dev \
    libomp-dev && \
    rm -rf /var/lib/apt/lists/*

# Create a virtual environment and install Python packages
RUN python -m venv /py && \
    /py/bin/pip install --upgrade pip && \
    /py/bin/pip install -r requirements.txt

# Add a non-root user
RUN adduser --disabled-password --no-create-home webapp

# Copy the application code before switching to the non-root user
COPY . .

# Set the PATH environment variable
ENV PATH="/py/bin:$PATH"

# Ensure the non-root user has access to the working directory
RUN chown -R webapp:webapp /gen_AI

# Switch to the non-root user
USER webapp

# Set the entry point and command for the container
ENTRYPOINT [ "/py/bin/streamlit", "run" ]
CMD [ "app.py" ]
