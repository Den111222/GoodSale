ARG VERSION=3.11
FROM python:${VERSION}

ARG WD=/opt/app
ARG GROUP=etl
ARG USER=etl

WORKDIR $WD

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONIOENCODING='utf-8'

#ENV PYTHONPATH 'opt/app/'

RUN groupadd -r $GROUP \
    && useradd -d $WD -r -g $GROUP $USER \
    && chown $USER:$GROUP -R $WD \
    && chown $USER:$GROUP /var/log

COPY --chown=$USER:$GROUP requirements.txt requirements.txt

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY --chown=$USER:$GROUP app .

#CMD ["python", "app/main.py"]
ENTRYPOINT ["python3", "main.py"]
#ENTRYPOINT ["tail", "-f", "/dev/null"]
