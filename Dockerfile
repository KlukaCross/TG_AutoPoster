FROM python:3.9-slim

VOLUME /data
WORKDIR /data

COPY setup.py README.md requirements.txt ./
ADD TG_AutoPoster TG_AutoPoster
RUN apt-get update && \
    apt-get install -y ffmpeg gcc musl-dev libxml2-dev libxslt-dev && \
    pip3 --no-cache-dir install --extra-index-url=https://www.piwheels.org/simple -r requirements.txt && \
    python3 setup.py install

ENTRYPOINT ["python3", "-m", "TG_AutoPoster"]
CMD []
