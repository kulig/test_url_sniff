ARG DOCKER_REGISTRY="docker.io"

ARG SERVICE_NAME="url-sniff"
ARG USER="${SERVICE_NAME}"
ARG WORKING_DIR="/opt/${SERVICE_NAME}"

ARG VIRTUAL_ENV="/opt/venv"


FROM ${DOCKER_REGISTRY}/python:3.9-slim-bullseye AS common

ARG VIRTUAL_ENV
ENV LANG=C.UTF-8 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    TZ="Europe/Moscow" \
    VIRTUAL_ENV=${VIRTUAL_ENV} \
    PATH="${VIRTUAL_ENV}/bin:${PATH}"


# production virtualenv
FROM common AS production-venv

RUN pip install --no-cache-dir poetry
COPY pyproject.toml poetry.lock ./

RUN python -m venv "${VIRTUAL_ENV}" \
    && poetry install --no-root --only main --no-interaction


# production
FROM common AS production

COPY --from=production-venv ${VIRTUAL_ENV} ${VIRTUAL_ENV}

ARG USER
RUN adduser --disabled-password --gecos '' ${USER}

ARG WORKING_DIR
COPY --chown=${USER}:${USER} . ${WORKING_DIR}
WORKDIR ${WORKING_DIR}

EXPOSE 8000

USER ${USER}
CMD ["uvicorn", "url_sniff:app", "--host", "0.0.0.0", "--port", "8000"]

# docker build --pull --target production --tag url-sniff:<version> .


# testing virtualenv
FROM production-venv AS testing-venv

RUN poetry install --no-root --only main,test --no-interaction


# testing
FROM common AS testing

COPY --from=testing-venv ${VIRTUAL_ENV} ${VIRTUAL_ENV}

ARG WORKING_DIR
COPY . ${WORKING_DIR}
WORKDIR ${WORKING_DIR}

# docker build --pull --target testing --tag url-sniff:<version>-tests .
