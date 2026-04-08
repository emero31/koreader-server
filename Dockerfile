# Použijeme inú, overenú verziu, ktorá je verejne dostupná bez hesla
FROM schmorp/koreader-sync:latest

# Tento server je v Pythone a je to ten "skutočný" originál
ENV PORT=10000
EXPOSE 10000

# Spustíme ho
CMD ["python", "koreader-sync.py", "0.0.0.0", "10000", "/data/koreader-sync-metadata.db"]
