#!/bin/bash
set -e

echo "==========================================="
echo "   Job Automator OCI Deployment Script     "
echo "==========================================="

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "[*] Docker not found. Installing Docker..."
    if [ -f /etc/debian_version ]; then
        # Ubuntu/Debian
        sudo apt-get update
        sudo apt-get install -y apt-transport-https ca-certificates curl software-properties-common
        curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
        echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
        sudo apt-get update
        sudo apt-get install -y docker-ce docker-ce-cli containerd.io
    elif [ -f /etc/oracle-release ]; then
        # Oracle Linux
        sudo dnf config-manager --add-repo=https://download.docker.com/linux/centos/docker-ce.repo
        sudo dnf install -y docker-ce docker-ce-cli containerd.io --nobest
        sudo systemctl enable --now docker
    else
        echo "[!] Unsupported OS. Please install Docker manually."
        exit 1
    fi
    sudo systemctl enable docker
    sudo systemctl start docker
    echo "[+] Docker installed successfully."
else
    echo "[+] Docker is already installed."
fi

# Check if Docker Compose is installed
if ! docker compose version &> /dev/null; then
    echo "[*] Docker Compose plugin not found. Installing..."
    if [ -f /etc/debian_version ]; then
        sudo apt-get install -y docker-compose-plugin
    elif [ -f /etc/oracle-release ]; then
        sudo dnf install -y docker-compose-plugin
    else
        echo "[!] Please install docker-compose-plugin manually."
        exit 1
    fi
    echo "[+] Docker Compose plugin installed."
fi

# Configure VM firewall (OCI VM local firewall override)
echo "[*] Configuring local OS firewall to open port 80..."
if command -v firewall-cmd &> /dev/null; then
    # Oracle Linux/CentOS
    sudo firewall-cmd --zone=public --add-service=http --permanent || true
    sudo firewall-cmd --zone=public --add-port=80/tcp --permanent || true
    sudo firewall-cmd --reload || true
elif command -v ufw &> /dev/null; then
    # Ubuntu UFW
    sudo ufw allow 80/tcp || true
    sudo ufw reload || true
fi

# Generic iptables rule just in case (OCI Ubuntu has strict default rules)
if command -v iptables &> /dev/null; then
    sudo iptables -I INPUT -p tcp --dport 80 -j ACCEPT || true
    if command -v netfilter-persistent &> /dev/null; then
        sudo netfilter-persistent save || true
    fi
fi
echo "[+] Firewall configured."

# Check if .env exists
if [ ! -f backend/.env ]; then
    echo "[*] Creating backend/.env from .env.example..."
    cp backend/.env.example backend/.env
    echo "[!] IMPORTANT: Please edit backend/.env with your secrets (especially TELEGRAM_BOT_TOKEN) before running."
    echo "    You can run: nano backend/.env"
    exit 0
fi

# Run docker-compose
echo "[*] Starting the application..."
docker compose build
docker compose up -d

echo "==========================================="
echo "[+] Deployment successful!"
echo "    App is running at: http://<your-vm-ip>"
echo "==========================================="
