# DigitalOcean Deployment Guide

## Prerequisites
- GitHub account (with the repository pushed)
- DigitalOcean account
- Docker and dependencies properly configured

## Deployment (Recommended: DigitalOcean App Platform)

### Step 1: Connect GitHub Repository
1. Go to [DigitalOcean Console](https://cloud.digitalocean.com)
2. Click **Create** → **Apps**
3. Select **GitHub** as the source
4. Authorize DigitalOcean to access your GitHub repositories
5. Choose `AI-Powered-Worker-Productivity-Dashboard` repository
6. Select `main` branch
7. Click **Next**

### Step 2: Configure App
1. DigitalOcean will auto-detect the `Dockerfile` in the root
2. Set the following environment variables:
   - `FLASK_ENV`: `production`
   - `FLASK_APP`: `app.py`
   - `PYTHONUNBUFFERED`: `1`

3. Configure HTTP routes:
   - Internal Port: **8080**
   - Routes: `/` (all traffic)

4. Click **Next**

### Step 3: Review & Deploy
1. Review the configuration
2. Enter an app name (e.g., `productivity-dashboard`)
3. Click **Create Resources**
4. Wait for deployment (~5-10 minutes)
5. Your app will be live at `https://your-app-name.ondigitalocean.app`

## Alternative: Using Docker on Droplets

### Step 1: Create a Droplet
- OS: Ubuntu 22.04 (LTS)
- Size: Basic ($6/month recommended)
- Add Docker 1-Click app

### Step 2: SSH & Clone Repository
```bash
ssh root@your-droplet-ip
git clone https://github.com/mudit-mohit/AI-Powered-Worker-Productivity-Dashboard.git
cd AI-Powered-Worker-Productivity-Dashboard
```

### Step 3: Build & Run
```bash
# Option 1: Using Docker Compose
docker-compose up -d

# Option 2: Using Docker directly
docker build -t productivity-dashboard .
docker run -d -p 80:8080 productivity-dashboard
```

### Step 4: Access Application
- Frontend & API: `http://your-droplet-ip`
- If using custom domain, point DNS to droplet IP

## Environment Variables

### Backend (Flask)
- `FLASK_ENV`: `production`
- `FLASK_APP`: `app.py`
- `PORT`: `8080` (auto-detected)
- `PYTHONUNBUFFERED`: `1`

## How the Application Works

- **Single Docker Container**: Both frontend and backend run together
- **Frontend Build**: React app is built during Docker build process
- **Backend Serves Frontend**: Flask serves the built React app at `/`
- **API Routes**: Backend API available at `/api/*`
- **Port**: Single port (8080) for all traffic

## Database

- **Type**: SQLite (file-based: `factory.db`)
- **Location**: Backend data directory
- **Persistence**: Data persists in DigitalOcean's container storage
- **Auto-initialization**: Database initializes on first run
- **Sample Data**: Auto-seeded with 7 days of sample events

## Monitoring & Logs

### App Platform
- View logs in DigitalOcean Console under "Logs" tab
- Monitor resource usage in "Metrics" tab
- Set up alerts for uptime monitoring

### Droplets
```bash
# View logs
docker logs <container-name>

# Monitor stats
docker stats

# SSH into droplet
ssh root@your-droplet-ip
```

## Scaling

- **App Platform**: Auto-scales based on traffic
- **Droplets**: Manually resize or add load balancing

## Cost Estimation

- **App Platform**: $12/month (shared resources)
- **Droplet ($6/month)**: Basic shared CPU
- **Droplet ($12/month)**: Better performance

## Troubleshooting

### Build Fails
- Check if `package.json` is in the `frontend` directory
- Verify `requirements.txt` is in the `backend` directory
- Ensure `Dockerfile` is in the repository root

### Application Won't Start
- Check logs for errors
- Verify environment variables are set
- Ensure database directory is writable

### API Not Responding
- Check if backend is running: `curl http://app-url/health`
- Verify database is initialized
- Check logs for connection errors

## Support & Documentation

- [DigitalOcean App Platform Docs](https://docs.digitalocean.com/products/app-platform/)
- [Docker on DigitalOcean](https://docs.digitalocean.com/products/droplets/)
- [GitHub Integration](https://docs.digitalocean.com/products/app-platform/how-to/connect-github-repo/)

