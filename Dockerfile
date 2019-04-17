FROM python:3.6

WORKDIR HW3

COPY ./requirements.txt /HW3/requirements.txt

RUN pip install -r requirements.txt

COPY . /HW3

RUN chmod +x startme.sh

CMD ["./startme.sh"]
