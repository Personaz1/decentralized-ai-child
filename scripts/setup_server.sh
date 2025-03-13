#!/bin/bash

# Exit on error
set -e

echo "Starting server setup for Decentralized AI System..."

# Update system
echo "Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install required packages
echo "Installing required packages..."
sudo apt install -y \
    python3.9 \
    python3.9-venv \
    python3.9-dev \
    git \
    nvidia-cuda-toolkit \
    nvidia-driver-535 \
    build-essential \
    curl \
    wget \
    ufw \
    nginx \
    certbot \
    python3-certbot-nginx

# Create project directories
echo "Creating project directories..."
sudo mkdir -p /opt/decentralized_ai/{src,config,models,cache,logs,data,backups}
sudo chown -R $USER:$USER /opt/decentralized_ai

# Clone repository
echo "Cloning repository..."
cd /opt/decentralized_ai
git clone https://github.com/your-username/decentralized-ai.git .

# Create virtual environment
echo "Setting up Python virtual environment..."
python3.9 -m venv venv
source venv/bin/activate

# Install dependencies
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Configure systemd service
echo "Configuring systemd service..."
cat << EOF | sudo tee /etc/systemd/system/decentralized-ai.service
[Unit]
Description=Decentralized AI System
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=/opt/decentralized_ai
Environment="PATH=/opt/decentralized_ai/venv/bin"
ExecStart=/opt/decentralized_ai/venv/bin/python src/main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Configure logging
echo "Setting up logging..."
sudo mkdir -p /var/log/decentralized-ai
sudo chown -R $USER:$USER /var/log/decentralized-ai

# Configure firewall
echo "Configuring firewall..."
sudo ufw allow 22  # SSH
sudo ufw allow 80  # HTTP
sudo ufw allow 443 # HTTPS
sudo ufw allow 9090  # Prometheus
sudo ufw allow 3000  # Grafana
sudo ufw --force enable

# Create backup script
echo "Creating backup script..."
cat << EOF > /opt/decentralized_ai/scripts/backup.sh
#!/bin/bash
BACKUP_DIR="/opt/decentralized_ai/backups"
DATE=\$(date +%Y%m%d_%H%M%S)
tar -czf \$BACKUP_DIR/backup_\$DATE.tar.gz /opt/decentralized_ai/{src,config,models}
find \$BACKUP_DIR -type f -mtime +7 -delete
EOF

chmod +x /opt/decentralized_ai/scripts/backup.sh

# Create restore script
echo "Creating restore script..."
cat << EOF > /opt/decentralized_ai/scripts/restore.sh
#!/bin/bash
if [ -z "\$1" ]; then
    echo "Usage: \$0 <backup_file>"
    exit 1
fi

BACKUP_FILE="\$1"
if [ ! -f "\$BACKUP_FILE" ]; then
    echo "Backup file not found: \$BACKUP_FILE"
    exit 1
fi

sudo systemctl stop decentralized-ai
tar -xzf "\$BACKUP_FILE" -C /
sudo systemctl start decentralized-ai
EOF

chmod +x /opt/decentralized_ai/scripts/restore.sh

# Set up automatic backups
echo "Setting up automatic backups..."
(crontab -l 2>/dev/null | grep -v "backup.sh"; echo "0 0 * * * /opt/decentralized_ai/scripts/backup.sh") | crontab -

# Reload systemd
echo "Reloading systemd..."
sudo systemctl daemon-reload

# Start service
echo "Starting service..."
sudo systemctl enable decentralized-ai
sudo systemctl start decentralized-ai

# Verify installation
echo "Verifying installation..."
sleep 5
if sudo systemctl is-active --quiet decentralized-ai; then
    echo "Service is running successfully"
else
    echo "Service failed to start. Check logs with: sudo journalctl -u decentralized-ai"
    exit 1
fi

# Check GPU
echo "Checking GPU..."
if command -v nvidia-smi &> /dev/null; then
    nvidia-smi
else
    echo "Warning: NVIDIA GPU not detected or drivers not installed"
fi

echo "Server setup completed successfully!"
echo "Next steps:"
echo "1. Configure your domain name in Nginx"
echo "2. Set up SSL certificate with Certbot"
echo "3. Configure monitoring with Prometheus and Grafana"
echo "4. Review security settings"
 