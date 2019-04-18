FROM centos:centos7
MAINTAINER jcrist

# Install supervisord
RUN curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py \
    && python get-pip.py \
    && pip install supervisor \
    && rm get-pip.py

# Install bzip and kerberos
RUN yum install -y \
        bzip2 \
        krb5-libs \
        krb5-server \
        krb5-workstation \
    && yum clean all \
    && rm -rf /var/cache/yum

# Copy over files
COPY ./files /

# Setup users for testing
RUN adduser -m alice \
    && adduser -m bob \
    && adduser -m carl \
    && kdb5_util create -s -P testpass \
    && kadmin.local -q "addprinc -randkey HTTP/address.example.com@EXAMPLE.COM" \
    && kadmin.local -q "addprinc -pw testpass alice" \
    && kadmin.local -q "addprinc -pw testpass bob" \
    && kadmin.local -q "addprinc -pw testpass carl" \
    && kadmin.local -q "xst -norandkey -k /root/users.keytab alice bob carl" \
    && kadmin.local -q "xst -norandkey -k /root/HTTP.keytab HTTP/address.example.com"

# Install miniconda
RUN curl https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh -o /tmp/miniconda.sh \
    && /bin/bash /tmp/miniconda.sh -b -p /opt/conda \
    && rm /tmp/miniconda.sh \
    && /opt/conda/bin/conda config --set always_yes yes --set changeps1 no

CMD ["supervisord", "--configuration", "/etc/supervisord.conf"]
