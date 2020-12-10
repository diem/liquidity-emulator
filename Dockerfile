FROM python:3.7-slim

WORKDIR /liquidity

RUN apt-get update && apt-get install -y gcc git
RUN apt-get install -y curl netcat
RUN pip install pipenv

COPY run.sh wait.sh ./
COPY Pipfile Pipfile.lock ./
RUN pipenv install --deploy --system

COPY account_watcher.py ./
COPY liquidity ./
COPY webapp ./

CMD ./run.sh
