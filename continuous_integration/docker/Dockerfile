FROM docker.io/library/alpine:3.23.4

RUN apk add --no-cache \
    gcc \
    git \
    krb5 \
    krb5-dev \
    krb5-server \
    linux-pam \
    musl-dev \
    npm \
    py3-pip \
    python3-dev \
    supervisor \
    # Can be compiled from pip, but quicker to use system packages:
    py3-krb5 \
    py3-python-gssapi

RUN npm install --global configurable-http-proxy

COPY ./files /

RUN mv /var/kerberos/krb5kdc/* /var/lib/krb5kdc/
# Setup users for testing
RUN adduser -D alice \
    && adduser -D bob \
    && adduser -D carl \
    && kdb5_util create -s -P testpass \
    && kadmin.local -q "addprinc -randkey HTTP/address.example.com@EXAMPLE.COM" \
    && kadmin.local -q "addprinc -pw testpass alice" \
    && kadmin.local -q "addprinc -pw testpass bob" \
    && kadmin.local -q "addprinc -pw testpass carl" \
    && kadmin.local -q "xst -norandkey -k /root/users.keytab alice bob carl" \
    && kadmin.local -q "xst -norandkey -k /root/HTTP.keytab HTTP/address.example.com"

RUN python3 -mvenv --system-site-packages /venv
# Allow mounting git directory with different owner
RUN git config --global --add safe.directory /working

CMD ["supervisord", "--configuration", "/etc/supervisord.conf"]

# docker run -it --rm --name ci -v ~/work/jupyter/kerberosauthenticator:/src -h address.example.com kerberosauthenticator-ci
# . /venv/bin/activate
# cd /src
# python3 -mpip install -r requirements.txt -r dev-requirements.txt

# python3 -mpip install -e . pytest-asyncio requests-kerberos
# python3 -mpytest --disable-warnings -x
