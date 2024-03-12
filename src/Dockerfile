FROM python:3.10.12

WORKDIR /readings/src

COPY . .


EXPOSE 8000

CMD ["sh", "-c", "uvicorn main:app --reload"]