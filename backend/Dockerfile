FROM python
WORKDIR /app
COPY ./requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt
COPY ./api /app/api
CMD uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload