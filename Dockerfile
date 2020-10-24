from dotriver/alpine-s6

ENV GOSU_VERSION 1.12

RUN apk --no-cache add sqlite python3 py3-pip py3-virtualenv jpeg-dev postgresql  \
	&&apk add --virtual .build-deps gcc musl-dev postgresql-dev libffi-dev python3-dev \
                                  make libevent-dev zlib-dev \
	&& virtualenv -p python3 /synapse \
	&& source /synapse/bin/activate \
	&& pip3 install --upgrade pip psycopg2 setuptools matrix-synapse \
	&& apk --purge del .build-deps

RUN apk add --no-cache --virtual .gosu-deps \
		ca-certificates \
		dpkg \
		gnupg \
	&& dpkgArch="$(dpkg --print-architecture | awk -F- '{ print $NF }')" \
	&& wget -O /usr/local/bin/gosu "https://github.com/tianon/gosu/releases/download/$GOSU_VERSION/gosu-$dpkgArch" \
	&& wget -O /usr/local/bin/gosu.asc "https://github.com/tianon/gosu/releases/download/$GOSU_VERSION/gosu-$dpkgArch.asc" \
	&& export GNUPGHOME="$(mktemp -d)" \
	&& gpg --batch --keyserver hkps://keys.openpgp.org --recv-keys B42F6819007F00F88E364FD4036A9C25BF357DD4 \
	&& gpg --batch --verify /usr/local/bin/gosu.asc /usr/local/bin/gosu \
	&& command -v gpgconf && gpgconf --kill all || : \
	&& rm -rf "$GNUPGHOME" /usr/local/bin/gosu.asc \
	&& apk del --no-network .gosu-deps \
	&& chmod +x /usr/local/bin/gosu \
	&& gosu --version \
	&& gosu nobody true

ADD conf/ /

RUN set -x \
    && chmod +x /etc/cont-init.d/ -R \
    && chmod +x /etc/periodic/ -R  \
    && chmod +x /etc/s6/services/ -R 
