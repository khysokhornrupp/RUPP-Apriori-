FROM tiangolo/uwsgi-nginx-flask:python3.8-alpine
ADD . /code
WORKDIR /code
RUN /usr/local/bin/python -m pip install --upgrade pip
RUN pip install -r requirements.txt
CMD python main.py


# FROM tiangolo/uwsgi-nginx-flask:python3.8-alpine
# RUN apk --update add bash nano
# ENV STATIC_URL /static
# ENV STATIC_PATH /var/www/app/static
# COPY ./requirements.txt /var/www/requirements.txt
# RUN /usr/local/bin/python -m pip install --upgrade pip
# RUN pip install -r /var/www/requirements.txt
