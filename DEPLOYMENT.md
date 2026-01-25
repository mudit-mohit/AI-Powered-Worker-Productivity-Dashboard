# Free Deployment Guide

This guide covers free deployment options for the AI-Powered Worker Productivity Dashboard.

## Best Free Option: Render ⭐

### Why Render?
- ✅ Free tier available (no credit card required)
- ✅ Native Docker support
- ✅ Auto-deploys from GitHub
- ✅ 750 free hours/month (enough for continuous deployment)
- ✅ Simple, fast setup

### Step-by-Step Deployment

#### 1. Create Render Account
- Go to [render.com](https://render.com)
- Sign up with GitHub (easiest)
- Authorize Render to access your repositories

#### 2. Create New Web Service
- Click **New +** → **Web Service**
- Select **AI-Powered-Worker-Productivity-Dashboard** repository
- Choose **Docker** as the runtime
- Click **Create Web Service**

#### 3. Configure Settings
- **Name**: `productivity-dashboard` (or your choice)
- **Environment**: Leave as default
- **Build Command**: (leave empty, uses Dockerfile)
- **Start Command**: (leave empty, uses Dockerfile CMD)

#### 4. Set Environment Variables
- Add the following in the "Environment" section:
  - `FLASK_ENV`: `production`
  - `FLASK_APP`: `app.py`
  - `PYTHONUNBUFFERED`: `1`
  - `PORT`: `8080`

#### 5. Deploy
- Click **Create Web Service**
- Render will auto-deploy from your GitHub repo
- Wait for build to complete (~5-10 minutes)
- Your app will be live at `https://productivity-dashboard.onrender.com`

### Free Tier Limits
- **Hours**: 750/month (covers 24/7 for ~25 days, spins down if unused)
- **Memory**: Shared
- **CPU**: Shared
- **Bandwidth**: Included
- **Custom Domain**: Supported (free)

---

## Alternative Options

### Railway.app
- Free $5/month credit (essentially free)
- [railway.app](https://railway.app) - Sign up with GitHub

### Oracle Cloud (Always Free)
- Truly free with no expiration
- [oracle.com/cloud/free](https://www.oracle.com/cloud/free/)

### Fly.io
- 3 free VMs included
- [fly.io](https://fly.io)

---

## Comparison Table

| Platform | Free Tier | Setup Time | Docker | Status |
|----------|-----------|-----------|--------|--------|
| **Render** | 750 hrs/mo | 5 min | ✅ | ⭐ Best |
| Railway | $5/month | 5 min | ✅ | Good |
| Oracle Cloud | Always free | 15 min | ✅ | Great |
| Fly.io | 3 free VMs | 10 min | ✅ | Good |

---

## Complete Render Setup

### 1. Sign Up
```
Visit: https://render.com
Click: Sign up with GitHub
```

### 2. Create Web Service
```
Dashboard → New → Web Service
Select: AI-Powered-Worker-Productivity-Dashboard
Runtime: Docker
```

### 3. Configuration
- **Name**: `productivity-dashboard`
- **Region**: Closest to you
- **Branch**: `main`
- **Build Command**: (empty)
- **Start Command**: (empty)

### 4. Environment Variables
```
FLASK_ENV = production
FLASK_APP = app.py
PYTHONUNBUFFERED = 1
PORT = 8080
```

### 5. Plan & Deploy
- **Plan**: Free
- **Auto-deploy**: On
- Click **Create Web Service**

### Access Your App
```
🌐 https://productivity-dashboard.onrender.com
📊 API: https://productivity-dashboard.onrender.com/api/dashboard
🏥 Health: https://productivity-dashboard.onrender.com/health
```

---

## Monitoring

### Check Deployment
1. Go to Render dashboard
2. Click your service
3. Watch the "Logs" tab during build
4. Once complete, your URL will be active

### View Logs
- **In Dashboard**: Real-time logs visible
- **Via CLI**: API endpoints accessible
- **Health Check**: `/health` endpoint

---

## Database

### Current Setup (SQLite)
- Stores data in `/app/data/factory.db`
- Data lost if service restarts (free tier limitation)
- Good for testing/demo purposes

### For Persistent Data
Connect to Render's free PostgreSQL database:
1. Create PostgreSQL in Render
2. Add database URL to environment variables
3. Update backend to use PostgreSQL instead of SQLite

---

## After Deployment

✅ App is live!

Next steps:
1. **Test it**: Visit your Render URL
2. **Monitor**: Check logs in dashboard
3. **Share**: Share the public URL with others
4. **Auto-deploy**: Every GitHub push auto-deploys

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Build fails | Check Render logs for error details |
| App won't start | Verify PORT=8080 env variable is set |
| Can't access app | Wait for build to complete (check logs) |
| API 404 errors | Ensure backend is running (check logs) |

---

## Free Tier Important Notes

- **Inactivity**: Service may spin down after 15 min of inactivity (spins up on next request)
- **Free hours**: 750 hours/month allows continuous running
- **No cost**: Truly free tier, no credit card needed
- **Performance**: Shared resources, suitable for personal projects

## Support

- [Render Docs](https://render.com/docs)
- [GitHub Integration](https://render.com/docs/github)
- [Troubleshooting](https://render.com/docs/troubleshooting)


