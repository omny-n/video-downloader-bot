FROM python:3.9
COPY /requirements.txt /app/requirements.txt 
WORKDIR /app
RUN pip install -r /app/requirements.txt
COPY . /app
CMD python /app/bot.py
ENTRYPOINT ["python", "bot.py"]