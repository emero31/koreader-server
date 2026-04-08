FROM python:3.9-slim

# Nastavíme pracovný priečinok
WORKDIR /app

# Skopírujeme tvoj python kód do vnútra kontajnera
COPY koreader-sync.py .

# Nastavíme port pre Render
ENV PORT=10000
EXPOSE 10000

# Spustíme tvoj kód
CMD ["python", "koreader-sync.py"]
