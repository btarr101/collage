FROM python:latest

WORKDIR /usr/src/collage

RUN pip install numpy pillow dropbox

COPY . .

CMD ["python", "./main.py"]