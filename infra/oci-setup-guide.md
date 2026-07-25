# Oracle Cloud Infrastructure (OCI) Split Deployment Guide

This guide describes how to deploy the **Job Automator** application using a high-performance **Split Architecture**. 

To host the entire application for free on OCI's AMD Micro shape (`VM.Standard.E2.1.Micro`), we offload memory-heavy components (Database, Cache, and Frontend) to specialized free tiers:
* 🖥️ **Frontend**: Vercel (Next.js hosting)
* ⚙️ **Backend & Scraper Workers**: OCI VM (FastAPI, Celery, Nginx)
* 🗄️ **Database**: Neon (Serverless Postgres)
* ⚡ **Cache & Queue**: Upstash (Serverless Redis)

---

## Step 1: Set Up Your External Free Tiers

### A. Neon Database (Postgres)
1. Visit [Neon.tech](https://neon.tech/) and sign up for a free account.
2. Create a new database project.
3. Copy your connection URI. You will need both the asynchronous and synchronous formats for your `.env` file:
   * **Asynchronous Database URL** (for FastAPI/Celery runtime):
     `postgresql+asyncpg://<username>:<password>@<neon_host>/neondb?sslmode=require`
   * **Synchronous Database URL** (for migrations):
     `postgresql://<username>:<password>@<neon_host>/neondb?sslmode=require`

### B. Upstash Redis (Queue)
1. Visit [Upstash.com](https://upstash.com/) and create a free account.
2. Create a new Serverless Redis database.
3. Copy the **Redis URL** from your database dashboard:
   `redis://default:<password>@<upstash_host>:<port>`

---

## Step 2: Deploy Frontend to Vercel
1. Visit [Vercel](https://vercel.com/) and sign up with your Git provider.
2. Select **Add New** → **Project** and import your project repository.
3. Under **Project Settings**:
   * Set **Root Directory** to `frontend`.
4. Expand the **Environment Variables** section and add:
   * **Name**: `NEXT_PUBLIC_API_URL`
   * **Value**: `http://<YOUR_OCI_VM_PUBLIC_IP>/api/v1` *(Note: If you plan to set up a custom domain with SSL later, change this to `https://yourdomain.com/api/v1`)*.
5. Click **Deploy**. Vercel will build and serve your Next.js application at a free `*.vercel.app` domain.

---

## Step 3: Launch OCI Always Free VM Instance
1. Log in to the [OCI Console](https://cloud.oracle.com/).
2. In the navigation menu, go to **Compute** → **Instances** and click **Create Instance**.
3. **Name**: Enter `job-automator-server`.
4. **Image and Shape**:
   * **Image**: Select `Ubuntu` (default/recommended) or `Oracle Linux`.
   * **Shape**: Select **VM.Standard.E2.1.Micro** (Always Free AMD shape, 1 OCPU, 1 GB RAM).
5. **Networking**: Ensure a **Public subnet** is selected, and check **Assign a public IPv4 address**.
6. **Add SSH Keys**: Select **Generate a key pair for me** and download the Private Key (`.key`).
7. Click **Create**. Once provisioned, copy the **Public IP Address**.

---

## Step 4: Configure Cloud & VM Firewall (Ingress Rules)
To allow Vercel and users to access the API on port 80:

### A. OCI Console (Virtual Cloud Network Firewall)
1. In the OCI Console, go to **Networking** → **Virtual Cloud Networks**.
2. Click on the VCN associated with your instance, and select **Public Subnet**.
3. Click on the associated **Default Security List**.
4. Click **Add Ingress Rules**:
   * **Source Type**: `CIDR`
   * **Source CIDR**: `0.0.0.0/0`
   * **IP Protocol**: `TCP`
   * **Destination Port Range**: `80`
   * **Description**: `Allow HTTP access to API / Nginx`
5. Click **Add Ingress Rules**.

---

## Step 5: Secure SSH Key & Connect to VM
On your local machine, set file permissions on your downloaded SSH key and log in:
```bash
# Secure the key file permissions
chmod 400 /path/to/your-ssh-key.key

# Connect via SSH (use 'ubuntu' for Ubuntu, or 'opc' for Oracle Linux)
ssh -i /path/to/your-ssh-key.key ubuntu@<YOUR_VM_PUBLIC_IP>
```

---

## Step 6: Configure a Swap File (Crucial for 1GB RAM)
Since the AMD shape only has 1GB of RAM, you **must** configure a swap file to provide virtual memory for Playwright/Chromium scraper tasks:
```bash
# Create a 4GB swap file
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# Make the swap permanent across VM reboots
echo '/swapfile swap swap defaults 0 0' | sudo tee -a /etc/fstab
```
*Run `free -h` to verify that `Swap: 4.0Gi` is successfully active.*

---

## Step 7: Transfer Project Files to the VM
Open a new terminal window **on your local machine** (not inside the SSH terminal) and run `rsync` to upload project files:
```bash
rsync -avz --exclude '.git' --exclude 'node_modules' --exclude '.venv' -e "ssh -i /path/to/your-ssh-key.key" ./ ubuntu@<YOUR_VM_PUBLIC_IP>:~/job-automator/
```

---

## Step 8: Configure Environment Variables on OCI
Switch back to your **SSH terminal** and create your environment file:
```bash
cd ~/job-automator

# Open the .env file
nano backend/.env
```
Fill in the configuration details:
```env
# Database (Neon connection strings)
DATABASE_URL=postgresql+asyncpg://<username>:<password>@<neon_host>/neondb?sslmode=require
DATABASE_URL_SYNC=postgresql://<username>:<password>@<neon_host>/neondb?sslmode=require

# Redis Cache & Queue (Upstash connection string)
REDIS_URL=redis://default:<password>@<upstash_host>:<port>/0

# Telegram Bot configuration
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id
```
Save and exit (`Ctrl+O`, `Enter`, `Ctrl+X`).

---

## Step 9: Start the Services
Run the OCI deploy script, which installs Docker and configures the host firewall, and then start the containers using `docker-compose-split.yml`:
```bash
# Initialize Docker and open local VM ports
sudo ./infra/deploy-oci.sh

# Build and start services using the split-architecture config
docker compose -f docker-compose-split.yml build
docker compose -f docker-compose-split.yml up -d
```

Your backend, Celery scraper workers, Celery beat scheduler, and Nginx reverse proxy will start running. 

* The backend API is exposed to Vercel at: `http://<YOUR_VM_PUBLIC_IP>/api/v1`
* The API interactive documentation is available at: `http://<YOUR_VM_PUBLIC_IP>/docs`
* Your Next.js Dashboard is live at your Vercel URL!

---

## Troubleshooting & Optimizations

### 1. Celery Worker Concurrency
By default, our `docker-compose-split.yml` configures Celery with `--concurrency=1`. **Do not increase this value** on a `VM.Standard.E2.1.Micro`. Limiting it to `1` ensures only one Playwright/Chromium scraper runs at any given time, preventing the system from running out of physical RAM.

### 2. Upgrading to SSL/HTTPS
If you want to secure the communication between Vercel and your OCI VM, you should purchase a domain name, point it to your VM's public IP, and install Certbot on your OCI VM to set up Let's Encrypt certificates. Update `/etc/nginx/conf.d/default.conf` to serve TLS on port 443.
