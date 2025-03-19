FROM ubuntu:16.04

# Install build tools and dependencies for Python
RUN apt-get update && \
    apt-get install -y vim-common dos2unix && \
    apt-get install -y \
    build-essential \
    libssl-dev \
    zlib1g-dev \
    libbz2-dev \
    libreadline-dev \
    libsqlite3-dev \
    wget \
    curl \
    llvm \
    libncurses5-dev \
    libncursesw5-dev \
    xz-utils \
    tk-dev \
    python3-pip \
    && apt-get clean

# Install Python 3.9 from source
RUN wget https://www.python.org/ftp/python/3.9.18/Python-3.9.18.tgz && \
    tar xvf Python-3.9.18.tgz && \
    cd Python-3.9.18 && \
    ./configure --enable-optimizations && \
    make -j$(nproc) && \
    make altinstall

# Set Python 3.9 as default python3
RUN ln -sf /usr/local/bin/python3.9 /usr/bin/python3 && \
    ln -sf /usr/local/bin/pip3.9 /usr/bin/pip3

# Set environment for gfortran portable (only PATH, NOT LD_LIBRARY_PATH to avoid Python conflicts)
ENV PORTABLE_GFORTRAN_PATH=/opt/gfortran_portable
ENV PATH="$PORTABLE_GFORTRAN_PATH/bin:$PATH"

# Set working directory
WORKDIR /app

# Copy gfortran portable libraries
COPY gfortran_portable/ /opt/gfortran_portable/

# Copy Fortran binary, Python API, requirements, and wrapper shell script
COPY emp_calc.x .
COPY emp_api.py .
COPY requirements.txt .
COPY run_emp_calc.sh .

# Ensure Fortran binary and wrapper script are executable
RUN chmod +x emp_calc.x run_emp_calc.sh

# Install Python dependencies with upgraded pip
RUN pip3 install --upgrade pip
RUN pip3 install --no-cache-dir -r requirements.txt

# Expose API port
EXPOSE 8000

# Run FastAPI app when container starts
CMD ["uvicorn", "emp_api:app", "--host", "0.0.0.0", "--port", "8000"]
