FROM ghcr.io/cmooon/kosync:latest
# Skúsime nechať port na Renderi, on si ho pridelí sám
CMD ["/app/kosync", "serve"]
