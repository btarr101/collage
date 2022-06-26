FROM python:latest

WORKDIR /usr/src/collage

RUN pip install --upgrade pip

RUN pip install\
    numpy   \
    pillow  \
    dropbox \
    beautifulsoup4 \
    defopt  \
    progressbar2

COPY . .

WORKDIR .