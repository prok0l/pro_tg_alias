FROM python:3.11
WORKDIR /Alias_bot
COPY requirements.txt /Alias_bot
RUN pip install -r requirements.txt
COPY . /Alias_bot