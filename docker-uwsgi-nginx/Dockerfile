FROM tiangolo/uwsgi-nginx:python3.7
MAINTAINER Dmitry Naumov <nda86@mail.ru>
# Add mc file manager and nano editor
RUN set -x \
        && apt-get update \
        && apt-get install --no-install-recommends --no-install-suggests -y  mc nano \
        && rm -rf /var/lib/apt/lists*

RUN rm -rf /app/*
COPY requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt

COPY supervisord.conf /etc/supervisor/conf.d/

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

COPY start.sh /start.sh
RUN chmod +x /start.sh

ENTRYPOINT ["/entrypoint.sh"]

CMD ["/start.sh"]
