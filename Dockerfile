FROM python:3.9-slim-buster as build

COPY requirements*.txt ./

# install deps
RUN set -ex; \
    apt-get update \
    && apt-get install -y --no-install-recommends \
    build-essential \
    python-dev \
    gcc \
    make \
    libffi-dev \
    libsasl2-dev \
    libxml2-dev \
    libxslt-dev \
    && pip install -r requirements.txt

FROM python:3.9-slim-buster

COPY --from=build /root/.cache /root/.cache
COPY --from=build requirements.txt .

RUN set -ex; \
    apt-get update \
    && apt-get install -y --no-install-recommends \
    bzip2 \
    ca-certificates \
    libffi6 \
    libsasl2-2 \
    libxml2 \
    libxslt1.1 \
    zlib1g \
    curl \
    gosu \
    unzip \
    libnspr4 \
    libnss3 \
    libexpat1 \
    libfontconfig1 \
    libuuid1 \
    \
    && pip install -r requirements.txt \
    && rm -rf /root/.cache \
    && rm -rf /var/lib/apt/lists/*


# create user for running this application
RUN set -ex; \
  groupadd --gid 1000 django && \
  useradd --uid 1000 --gid django --shell /bin/bash --create-home django

RUN mkdir app
WORKDIR app

EXPOSE 8000

COPY ./ /app/

COPY start-lukis.sh /usr/local/bin/start-lukis.sh

CMD ["/usr/local/bin/start-lukis.sh"]
