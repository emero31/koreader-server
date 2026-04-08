FROM ghcr.io/cmooon/kosync:latest
ENV PORT=7200
EXPOSE 7200
CMD ["/app/kosync", "serve"]
