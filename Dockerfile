FROM python:3.12.4-slim
WORKDIR /app/

# Setup environment
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

# Copy the rest of the project except what is in .dockerignore
COPY . /app/

EXPOSE 8200

RUN apt update && apt-get -y install netcat-traditional

RUN pip install -r requirements.txt

# Run the application
CMD ["sh", "scripts/run.sh"]