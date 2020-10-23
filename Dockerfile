from dotriver/alpine-s6


RUN apk --no-cache add python3 py3-pip py3-virtualenv jpeg-dev postgresql &&\
    apk add --virtual .build-deps gcc musl-dev postgresql-dev libffi-dev python3-dev \
                                  make libevent-dev zlib-dev &&\
    \
    virtualenv -p python3 /synapse &&\
    source /synapse/bin/activate &&\
    \
    pip3 install --upgrade pip &&\
    pip3 install --upgrade psycopg2 &&\
    pip3 install --upgrade setuptools &&\
    pip3 install matrix-synapse &&\
    pip3 install matrix-synapse-ldap3 &&\
    apk --purge del .build-deps

ENV GOSU_VERSION 1.12
RUN set -eux; \
	\
	apk add --no-cache --virtual .gosu-deps \
		ca-certificates \
		dpkg \
		gnupg \
	; \
	\
	dpkgArch="$(dpkg --print-architecture | awk -F- '{ print $NF }')"; \
	wget -O /usr/local/bin/gosu "https://github.com/tianon/gosu/releases/download/$GOSU_VERSION/gosu-$dpkgArch"; \
	wget -O /usr/local/bin/gosu.asc "https://github.com/tianon/gosu/releases/download/$GOSU_VERSION/gosu-$dpkgArch.asc"; \
	\
# verify the signature
	export GNUPGHOME="$(mktemp -d)"; \
	gpg --batch --keyserver hkps://keys.openpgp.org --recv-keys B42F6819007F00F88E364FD4036A9C25BF357DD4; \
	gpg --batch --verify /usr/local/bin/gosu.asc /usr/local/bin/gosu; \
	command -v gpgconf && gpgconf --kill all || :; \
	rm -rf "$GNUPGHOME" /usr/local/bin/gosu.asc; \
	\
# clean up fetch dependencies
	apk del --no-network .gosu-deps; \
	\
	chmod +x /usr/local/bin/gosu; \
# verify that the binary works
	gosu --version; \
	gosu nobody true

ADD conf/ /

