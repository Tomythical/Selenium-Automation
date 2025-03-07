# Stage 1: Build the Go application
FROM golang:1.24 AS builder

WORKDIR /app

# Copy go.mod and go.sum to download dependencies
COPY go.mod go.sum ./
RUN go mod download

# Copy the rest of the application
COPY cmd/* ./

# Build the binary
RUN go build -o app

FROM ghcr.io/go-rod/rod AS rod

# Set the correct base image dynamically
WORKDIR /app

# Copy the built Go binary from the builder stage
COPY --from=builder /app/app .

# Run the application
ENTRYPOINT ["./app"]
