FROM golang:1.21-alpine AS builder

WORKDIR /app

# Copy go files
COPY main.go .

# Download dependencies
RUN go mod init hello-api && \
    go get github.com/lib/pq && \
    go build -o api main.go

FROM alpine:latest

WORKDIR /root/

COPY --from=builder /app/api .

EXPOSE 8080

CMD ["./api"]
