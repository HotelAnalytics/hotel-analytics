FROM fedora:23

RUN ln -sf /usr/share/zoneinfo/US/Central /etc/localtime

RUN ["dnf", "install", "-y", "tar", "wget", "gcc", "gcc-c++", "openssl", "file", "mariadb-devel", "freetds", "unixODBC", "unixODBC-devel", "python3", "python3-pip", "python3-devel", "python3-psycopg2", "redhat-rpm-config", "numpy", "scipy", "libxml2-devel", "libxslt-devel", "libffi-devel", "libpqxx-devel"]

RUN dnf clean all

# Python 3 Setup
ADD pip.conf /etc/pip.conf
ADD setup_python.sh /tmp/setup_python.sh

RUN chmod +x /tmp/setup_python.sh
RUN /tmp/setup_python.sh

WORKDIR /app/

ADD requirements.txt /app/requirements.txt
RUN ["pip", "install", "-r", "requirements.txt", "--find-links=http://packages.hotel-analytics.com/python/", "--trusted-host", "packages.hotel-analytics.com"]

ADD . /app/

EXPOSE 80
CMD ["gunicorn", "-b 0.0.0.0:80", "--log-file=-", "api:app"]
