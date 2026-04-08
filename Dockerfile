FROM ghcr.io/cmooon/kosync:latest

# Povieme serveru, aby počúval na porte, ktorý mu pridelí Render
CMD ["/app/kosync", "serve", "--port", "10000", "--address", "0.0.0.0"]
