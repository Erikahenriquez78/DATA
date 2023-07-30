FROM python:3.11.1
WORKDIR /app
COPY ./app .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
EXPOSE 5000
CMD ["python", "api_model.py"]