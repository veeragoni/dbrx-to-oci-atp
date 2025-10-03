FROM fnproject/python:3.11-dev AS build-stage

WORKDIR /function

# Install build dependencies (gcc, g++, make, perl, pkg-config for compiling Rust packages)
RUN microdnf install -y gcc gcc-c++ make perl openssl-devel pkg-config libffi-devel && \
    microdnf clean all && \
    pip install --upgrade pip

# Copy requirements and install dependencies
COPY requirements.txt /function/
# Use --only-binary to force using pre-built wheels and avoid compilation issues
RUN pip install --target /python/ --no-cache-dir --only-binary=:all: -r requirements.txt || \
    pip install --target /python/ --no-cache-dir -r requirements.txt

# Final stage
FROM fnproject/python:3.11

WORKDIR /function

# Copy dependencies from build stage
COPY --from=build-stage /python /python

# Copy function code
COPY func.py /function/

# Copy Oracle wallet for ATP connection
COPY Wallet_NDG3D3LXZ4ESODQC /function/wallet/

# Set environment
ENV PYTHONPATH=/python
ENV TNS_ADMIN=/function/wallet

ENTRYPOINT ["/python/bin/fdk", "/function/func.py", "handler"]
