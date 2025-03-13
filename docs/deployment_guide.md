# Deployment Guide

This guide provides detailed instructions for deploying the Decentralized AI System on a production server.

## Server Requirements

### Minimum Requirements:
- 4 CPU cores
- 16GB RAM
- 100GB SSD
- NVIDIA GPU with 8GB VRAM
- Ubuntu 22.04 LTS

### Recommended Requirements:
- 8 CPU cores
- 32GB RAM
- 500GB SSD
- NVIDIA RTX 3080 or better
- Ubuntu 22.04 LTS

## Deployment Steps

### 1. Server Rental
1. Choose a cloud provider (AWS, Google Cloud, DigitalOcean)
2. Create an instance with Ubuntu 22.04 LTS
3. Select the appropriate configuration
4. Save your SSH keys and IP address

### 2. Connect to Server
```bash
ssh -i your-key.pem ubuntu@your-server-ip
```

### 3. Server Setup
```bash
# Download setup script
wget https://raw.githubusercontent.com/your-username/decentralized-ai/main/scripts/setup_server.sh

# Make it executable
chmod +x setup_server.sh

# Run the script
./setup_server.sh
```

### 4. Verify Installation
```bash
# Check service status
sudo systemctl status decentralized-ai

# View logs
sudo journalctl -u decentralized-ai -f

# Check GPU availability
nvidia-smi
```

### 5. Monitoring Setup
```bash
# Open required ports
sudo ufw allow 22  # SSH
sudo ufw allow 80  # HTTP
sudo ufw allow 443 # HTTPS
sudo ufw allow 9090  # Prometheus
sudo ufw allow 3000  # Grafana

# Check port availability
sudo ufw status
```

## System Management

### Start/Stop Service
```bash
# Start service
sudo systemctl start decentralized-ai

# Stop service
sudo systemctl stop decentralized-ai

# Restart service
sudo systemctl restart decentralized-ai
```

### View Logs
```bash
# View real-time logs
sudo journalctl -u decentralized-ai -f

# View last 100 lines
sudo journalctl -u decentralized-ai -n 100
```

### Update System
```bash
# Pull latest changes
cd /opt/decentralized_ai
git pull

# Update dependencies
source venv/bin/activate
pip install -r requirements.txt

# Restart service
sudo systemctl restart decentralized-ai
```

## Security Configuration

### Firewall Setup
```bash
# Enable firewall
sudo ufw enable

# Allow SSH
sudo ufw allow ssh

# Allow application ports
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
```

### SSL Setup
```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d your-domain.com
```

## Monitoring

### Metrics
- System metrics available at: http://your-server-ip:9090
- Grafana dashboards at: http://your-server-ip:3000

### Key Metrics to Monitor
- CPU usage
- Memory usage
- GPU utilization
- Disk space
- Network traffic
- API response times
- Error rates

## Backup Procedures

### Create Backup Directory
```bash
sudo mkdir -p /opt/decentralized_ai/backups
sudo chown -R ubuntu:ubuntu /opt/decentralized_ai/backups
```

### Set Permissions
```bash
sudo chmod 700 /opt/decentralized_ai/backups
```

### Automate Backups
```bash
# Add to crontab
0 0 * * * /opt/decentralized_ai/scripts/backup.sh
```

## Troubleshooting

### Check Service Status
```bash
# Check service status
sudo systemctl status decentralized-ai

# Check resource usage
htop
nvidia-smi
```

### Common Issues

#### Memory Issues
```bash
# Check memory usage
free -h

# Check swap usage
swapon --show
```

#### GPU Issues
```bash
# Check GPU status
nvidia-smi

# Check CUDA installation
nvcc --version
```

#### Network Issues
```bash
# Check network connectivity
ping google.com

# Check open ports
sudo netstat -tulpn
```

### Log Analysis
```bash
# Check error logs
sudo journalctl -u decentralized-ai -p err

# Check recent logs
sudo journalctl -u decentralized-ai --since "1 hour ago"
```

## Maintenance

### Regular Tasks
1. Monitor system logs daily
2. Check backup status weekly
3. Update system monthly
4. Review security patches weekly
5. Monitor resource usage daily

### Performance Optimization
1. Monitor and adjust cache settings
2. Optimize database queries
3. Review and adjust worker processes
4. Monitor and adjust memory limits

## Support

For deployment issues:
1. Check the logs
2. Review the documentation
3. Contact system administrator
4. Create an issue on GitHub

## Rollback Procedures

### Backup Restoration
```bash
# Stop service
sudo systemctl stop decentralized-ai

# Restore from backup
/opt/decentralized_ai/scripts/restore.sh /path/to/backup

# Start service
sudo systemctl start decentralized-ai
```

### Version Rollback
```bash
# Check available versions
git tag

# Rollback to specific version
git checkout v1.0.0

# Restart service
sudo systemctl restart decentralized-ai
``` 