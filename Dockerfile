# Étape de construction pour Go
FROM golang:1.21-alpine as go-builder

WORKDIR /app
COPY go/go.mod .
RUN go mod download

COPY go/ .
RUN CGO_ENABLED=0 GOOS=linux go build -o server .

# Étape de construction pour Python
FROM python:3.9-alpine as python-builder

WORKDIR /app
COPY python/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY python/app.py .

# Étape finale
FROM python:3.9-alpine

WORKDIR /app

# Copier les binaires et dépendances
COPY --from=go-builder /app/server .
COPY --from=python-builder /usr/local/lib/python3.9/site-packages /usr/local/lib/python3.9/site-packages
COPY --from=python-builder /app/app.py /app/python/app.py

# Copier les fichiers statiques
COPY frontend/ /app/frontend/
COPY go/certs/ /app/certs/

# Créer les répertoires temporaires
RUN mkdir -p /app/tmp/uploads /app/tmp/output

# Installation des dépendances système pour pdfplumber
RUN apk add --no-cache gcc musl-dev python3-dev jpeg-dev zlib-dev

EXPOSE 8443

CMD ["/app/server"]