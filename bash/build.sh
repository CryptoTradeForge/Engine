#!/bin/bash
IMAGE_NAME="binance-trade"
IMAGE_TAG="latest"
CONTAINER_NAME="binance-trade-container"
MOUNT_PATH="/app"
CURRENT_DIR=$(pwd)

if [[ ! -f "${CURRENT_DIR}/.env" ]]; then
    if [[ -f "${CURRENT_DIR}/.env.example" ]]; then
        echo ".env file not found. Copying .env.example to .env..."
        cp "${CURRENT_DIR}/.env.example" "${CURRENT_DIR}/.env"
        echo ".env file created successfully."
    else
        echo "Error: .env.example not found. Cannot create .env file."
        exit 1
    fi
else
    echo ".env file already exists. Skipping .env creation."
fi

if [[ "$(docker images -q ${IMAGE_NAME}:${IMAGE_TAG} 2> /dev/null)" == "" ]]; then
    echo "Docker image $IMAGE_NAME:$IMAGE_TAG not found. Building the image..."
    docker build -t "$IMAGE_NAME:$IMAGE_TAG" .
    
    if [ $? -eq 0 ]; then
        echo "Docker image $IMAGE_NAME:$IMAGE_TAG built successfully."
    else
        echo "Failed to build Docker image."
        exit 1
    fi
else
    echo "Docker image $IMAGE_NAME:$IMAGE_TAG already exists. Skipping build."
fi

if [[ "$(docker ps -q -f name=${CONTAINER_NAME})" == "" ]]; then
    echo "Starting a new container named $CONTAINER_NAME..."
    docker run --name "$CONTAINER_NAME" -it -v "${CURRENT_DIR}:${MOUNT_PATH}" "$IMAGE_NAME:$IMAGE_TAG"
else
    echo "A container named $CONTAINER_NAME is already running."
    echo "To mount a new path, stop the container and rerun the script."
fi
