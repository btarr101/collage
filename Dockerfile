FROM python:3.10

WORKDIR ../collage

ADD config.py .
ADD util.py .
ADD dropboxManager.py .
ADD preProcess.py .
ADD genCollages.py .
ADD main.py .
RUN mkdir "tmp"

RUN pip install numpy pillow dropbox

CMD ["python", "./main.py"]