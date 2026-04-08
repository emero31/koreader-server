FROM ghcr.io/cmooon/kosync:latest

# Render vyžaduje, aby sme počúvali na porte 10000 alebo ho aspoň definovali
ENV PORT=10000
EXPOSE 10000

# Spustíme server a povieme mu, nech počúva na porte 10000 a adrese 0.0.0.0
CMD ["/app/kosync", "serve", "--port", "10000", "--address", "0.0.0.0"]
