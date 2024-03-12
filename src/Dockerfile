FROM python:3.10.12

WORKDIR /readings/src

COPY . .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN pip install joblib
RUN pip install scikit-surprise

EXPOSE 8000

CMD ["sh", "-c", "uvicorn main:app --reload"]