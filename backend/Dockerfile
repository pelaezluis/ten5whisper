FROM tiangolo/uvicorn-gunicorn-fastapi:python3.10-2022-11-25
ENV PYTHONUNBUFFERED=1
ENV POETRY_VERSION=1.1.14

WORKDIR /code
# Install Poetry
RUN apt clean && apt update && apt install libsndfile1 ffmpeg libgstreamer1.0-0 libsndfile1-dev libgirepository1.0-dev gstreamer1.0-plugins-base gstreamer1.0-plugins-ugly wkhtmltopdf -y

COPY app/pyproject.toml app/poetry.lock* /code/

# Allow installing dev dependencies to run tests
RUN pip install poetry
RUN poetry config virtualenvs.create false
RUN poetry install

ARG INSTALL_JUPYTER=false
RUN bash -c "if [ $INSTALL_JUPYTER == 'true' ] ; then pip install jupyterlab ; fi"


ENV PYTHONPATH=/code
EXPOSE 8000

