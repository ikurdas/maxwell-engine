# Use the official Python 3.10 image
FROM python:3.10-slim

# Set the working directory
WORKDIR /code

# Copy requirements and install
COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# Copy the entire project
COPY . /code

# Create a non-root user (HuggingFace Spaces requirement)
RUN useradd -m -u 1000 user
USER user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH

WORKDIR $HOME/app
COPY --chown=user . $HOME/app

# HuggingFace Spaces strictly requires apps to run on port 7860
# This command overrides the 3141 port inside app.py and runs it on 7860 for the cloud.
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "7860"]
