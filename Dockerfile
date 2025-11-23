
FROM python:3.14-slim-bookworm

# latest version from docs, but not "latest" for reproducibility
COPY --from=ghcr.io/astral-sh/uv:0.9.11 /uv /uvx /bin/

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

COPY pyproject.toml uv.lock ./

# ex pip install -r requireemnts.txt
RUN uv sync --frozen --no-install-project

COPY . .

# for streamlit. But to be defined later
EXPOSE 8051

CMD ["uv", "run", "streamlit", "run", "src/app.py", "--server.port=8501", "--server.address=0.0.0.0"]