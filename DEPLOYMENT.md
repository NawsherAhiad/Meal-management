# Deployment Guide - 24/7 Free Hosting

This guide will help you deploy your Meal Management System to Render.com (free tier with 24/7 uptime).

## Option 1: Render.com (Recommended - Free 24/7)

### Step 1: Create GitHub Repository

1. Go to [GitHub](https://github.com) and create a new repository
2. Initialize git in your project folder:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
   git push -u origin main
   ```

### Step 2: Deploy on Render

1. Go to [Render.com](https://render.com) and sign up/login
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Configure the service:
   - **Name**: meal-management (or any name you prefer)
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
   - **Plan**: Free (spins down after 15 min inactivity, but wakes up on request)

### Step 3: Set Up PostgreSQL Database

1. In Render dashboard, click "New +" → "PostgreSQL"
2. Configure:
   - **Name**: mealmanagement-db
   - **Database**: mealmanagement
   - **User**: mealmanagement
   - **Plan**: Free (512 MB storage)
3. Copy the **Internal Database URL**

### Step 4: Configure Environment Variables

In your Web Service settings, add these environment variables:

- **DATABASE_URL**: Paste the PostgreSQL connection string from step 3
- **SECRET_KEY**: Generate a random string (you can use: `python -c "import secrets; print(secrets.token_hex(32))"`)
- **ADMIN_PASSWORD**: Set your admin password (e.g., `your-secure-password`)
- **FLASK_DEBUG**: `False`

### Step 5: Deploy

1. Click "Create Web Service"
2. Wait for deployment to complete (5-10 minutes)
3. Your app will be live at: `https://your-app-name.onrender.com`

**Note**: Free tier on Render may take 30-60 seconds to wake up if inactive for 15+ minutes.

---

## Option 2: Railway.app (Alternative - Free 24/7)

### Step 1: Deploy to Railway

1. Go to [Railway.app](https://railway.app) and sign up/login
2. Click "New Project" → "Deploy from GitHub repo"
3. Select your repository
4. Railway will auto-detect Python and deploy

### Step 2: Add PostgreSQL

1. Click "+ New" → "Database" → "Add PostgreSQL"
2. Railway will automatically set `DATABASE_URL` environment variable

### Step 3: Set Environment Variables

In your project settings, add:
- **SECRET_KEY**: Generate random string
- **ADMIN_PASSWORD**: Your admin password
- **FLASK_DEBUG**: `False`

### Step 4: Get Your URL

Railway will provide a URL like: `https://your-app-name.up.railway.app`

---

## Option 3: Fly.io (Free Tier with Persistent 24/7)

1. Install Fly CLI: `iwr https://fly.io/install.ps1 -useb | iex`
2. Login: `fly auth login`
3. Initialize: `fly launch`
4. Deploy: `fly deploy`

---

## Important Notes:

1. **Database**: Make sure to use PostgreSQL connection string, not SQLite
2. **Secret Key**: Use a strong, random secret key in production
3. **Admin Password**: Change the default admin password
4. **Free Tier Limitations**:
   - Render: Spins down after 15 min, wakes on request
   - Railway: Limited hours per month
   - Fly.io: Best for true 24/7, but more complex setup

## Quick Deploy Commands (Render):

```bash
# 1. Push to GitHub
git add .
git commit -m "Ready for deployment"
git push

# 2. Go to Render.com and follow the steps above
```

## Testing After Deployment:

1. Visit your live URL
2. Test adding a member
3. Test meal tracking
4. Test admin login
5. Test PDF export

---

## Troubleshooting:

- **Database connection errors**: Check DATABASE_URL is correct
- **App won't start**: Check build logs in Render dashboard
- **500 errors**: Check application logs in Render dashboard
- **Slow first load**: Normal on free tier (cold start)

---

## Upgrade to Always-On (Paid):

If you need true 24/7 without cold starts:
- **Render**: $7/month for always-on
- **Railway**: $5/month for always-on
- **Fly.io**: Pay-as-you-go, very affordable
