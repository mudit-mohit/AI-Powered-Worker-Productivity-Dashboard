# DigitalOcean Deployment Guide

## Prerequisites
- GitHub account (with the repository pushed)
- DigitalOcean account
- Docker images built and ready

## Deployment Options

### Option 1: Using DigitalOcean App Platform (Recommended)

1. **Go to DigitalOcean Console**
   - Log in to [DigitalOcean](https://cloud.digitalocean.com)
   - Click "Create" → "Apps"

2. **Connect GitHub Repository**
   - Select your GitHub account
   - Choose `AI-Powered-Worker-Productivity-Dashboard` repository
   - Branch: `main`

3. **Configure Services**
   - DigitalOcean will auto-detect `app.yaml`
   - Review the backend and frontend configurations
   - Ensure environment variables are set correctly

4. **Deploy**
   - Click "Create Resources"
   - Wait for deployment to complete (~5-10 minutes)
   - Your app will be live at a `.ondigitalocean.app` domain

### Option 2: Using Docker on Droplets

1. **Create a Droplet**
   - OS: Ubuntu 22.04 (LTS)
   - Size: Basic ($6/month recommended)
   - Add Docker 1-Click app for easy setup

2. **Connect via SSH**
   ```bash
   ssh root@your-droplet-ip
   ```

3. **Clone Repository**
   ```bash
   git clone https://github.com/mudit-mohit/AI-Powered-Worker-Productivity-Dashboard.git
   cd AI-Powered-Worker-Productivity-Dashboard
   ```

4. **Build and Run with Docker Compose**
   ```bash
   docker-compose up -d
   ```

5. **Access Application**
   - Backend: `http://your-droplet-ip:5000`
   - Frontend: `http://your-droplet-ip:3000`

6. **Setup Domain (Optional)**
   - Add your domain in DigitalOcean DNS settings
   - Point to your droplet's IP

### Option 3: Using DigitalOcean Kubernetes

1. **Create Kubernetes Cluster**
   - DigitalOcean Dashboard → Kubernetes
   - Create a new cluster (3 nodes recommended)

2. **Deploy with Helm**
   ```bash
   helm install productivity-dashboard ./k8s
   ```

## Environment Variables

### Backend
- `FLASK_ENV`: `production`
- `FLASK_APP`: `app.py`
- `PORT`: (auto-detected by DigitalOcean)

### Frontend
- `REACT_APP_API_URL`: Backend API URL (e.g., `https://app-name.ondigitalocean.app/api`)
- `NODE_ENV`: `production`

## Database

SQLite database is stored in `/app/data` directory. For production, consider:
- Using PostgreSQL on DigitalOcean Managed Database
- Mounting persistent volumes in Kubernetes
- Regular backups

## Monitoring & Logs

### App Platform
- View logs in DigitalOcean Console
- Monitor metrics and resource usage
- Set up alerts for uptime

### Droplets
- SSH into droplet: `ssh root@your-droplet-ip`
- View logs: `docker logs productivity-backend` or `docker logs productivity-frontend`
- Monitor: `docker stats`

## Scaling

- **App Platform**: Auto-scales based on demand
- **Droplets**: Scale manually by resizing or adding more droplets
- **Kubernetes**: Auto-scaling configured in cluster

## Cost Estimation

- **App Platform**: $12/month (shared resources)
- **Droplet**: $6-24/month (depending on size)
- **Managed Database (optional)**: $15+/month
- **Bandwidth**: Usually included

## Support & Documentation

- [DigitalOcean App Platform Docs](https://docs.digitalocean.com/products/app-platform/)
- [Docker on DigitalOcean](https://docs.digitalocean.com/products/droplets/)
- [Kubernetes on DigitalOcean](https://docs.digitalocean.com/products/kubernetes/)
