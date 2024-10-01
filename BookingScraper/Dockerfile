FROM mcr.microsoft.com/playwright/python:v1.38.0-jammy

WORKDIR /BookingScraper

RUN pip install playwright pandas openpyxl
RUN playwright install chromium

COPY . /BookingScraper


CMD ["python3", "main.py"]
