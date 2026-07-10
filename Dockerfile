# Backend image for Hugging Face Spaces (Docker SDK, port 7860)
FROM python:3.12-slim

WORKDIR /code
COPY pyproject.toml uv.lock ./
RUN pip install --no-cache-dir uv \
    && uv export --no-dev --frozen --format requirements.txt > requirements.txt \
    && pip install --no-cache-dir -r requirements.txt \
    && pip uninstall -y uv

# The knowledge base lives in MongoDB Atlas at runtime; kb/ is build-time only.
COPY app ./app

ENV PORT=7860
EXPOSE 7860
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7860"]
