FROM python:3.10-bullseye

WORKDIR /code

# Install packages
COPY ./requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["python3", "-m", "bot"]
