FROM python:3.6

# Install git
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

COPY . .
## Clone the repository
#RUN git clone https://github.com/MISP/threat-actor-intelligence-server /app

# Initialize and update submodules
RUN git submodule init && git submodule update

# Install dependencies
RUN pip install --no-cache-dir -r REQUIREMENTS

# Expose the port the server listens on
EXPOSE 8889

WORKDIR /app/bin

# Entrypoint
ENTRYPOINT ["python", "tai-server.py"]
