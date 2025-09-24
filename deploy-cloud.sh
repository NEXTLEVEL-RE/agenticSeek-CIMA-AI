#!/bin/bash
# deploy-cloud.sh: Deploy agenticSeek to a fresh Ubuntu cloud VM
# Usage: bash deploy-cloud.sh <GIT_REPO_URL> <APP_DIR>
# Example: bash deploy-cloud.sh https://github.com/yourusername/agenticSeek.git agenticSeek

set -e

if [ "$#" -ne 2 ]; then
  echo "Usage: $0 <GIT_REPO_URL> <APP_DIR>"
  exit 1
fi

GIT_REPO_URL="$1"
APP_DIR="$2"

# 1. Update system and install dependencies
sudo apt update
sudo apt install -y git docker.io docker-compose
sudo systemctl start docker
sudo systemctl enable docker

# 2. Clone the repository
if [ ! -d "$APP_DIR" ]; then
  git clone "$GIT_REPO_URL" "$APP_DIR"
fi
cd "$APP_DIR"

# 3. (Optional) Pull latest changes
# git pull origin main

# 4. Build and start the app with Docker Compose
sudo docker-compose up --build -d

echo "\n---\nDeployment complete!"
echo "App should be available at: http://<your-server-ip>"
echo "API docs: http://<your-server-ip>:8000/docs"
echo "---\n" 