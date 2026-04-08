FROM ghcr.io/cmooon/kosync:latest

# Nastavenie portu, ktory Render vyzaduje
ENV PORT=7200
EXPOSE 7200

# Spustenie servera
CMD ["/app/kosync", "serve"]
