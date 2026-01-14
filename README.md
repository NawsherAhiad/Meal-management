# Banasree Boys - Meal Management System

A web application for tracking daily meals for members with PDF export functionality.

## Features

- **Add Members**: Simple form to add new members to the system
- **Weekly Meal Tracking**: Track meals for 7 days with dropdown selection (0-5 meals)
- **PDF Export**: Export monthly meal reports as PDF showing totals per member
- **Admin Panel**: Edit past meal records (admin-only access)
- **Mobile Responsive**: Beautiful UI that works on all devices
- **No Login Required**: Regular users can access and add meals without login
- **Daily Reset**: Meal tracking resets daily (shows null/0 for new days)

## Tech Stack

- **Backend**: Python (Flask)
- **Database**: PostgreSQL
- **PDF Generation**: ReportLab
- **Frontend**: HTML, CSS, JavaScript

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up PostgreSQL Database

You can use any free PostgreSQL hosting service:

- **Supabase** (Recommended): https://supabase.com
- **Railway**: https://railway.app
- **Render**: https://render.com
- **Neon**: https://neon.tech

After creating your database, copy the connection string.

### 3. Configure Environment Variables

Create a `.env` file in the root directory:

```env
DATABASE_URL=postgresql://username:password@host:port/database_name
SECRET_KEY=your-secret-key-change-this-in-production
ADMIN_PASSWORD=admin123
```

### 4. Run the Application

```bash
python app.py
```

The application will be available at `http://localhost:5000`

## 🚀 Quick Deployment (24/7 Free Hosting)

### Recommended: Render.com (Easiest)

1. **Push to GitHub**:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
   git push -u origin main
   ```

2. **Deploy on Render**:
   - Go to [render.com](https://render.com) and sign up
   - Click "New +" → "Web Service"
   - Connect your GitHub repo
   - Settings:
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `gunicorn app:app`
   - Click "Create Web Service"

3. **Add PostgreSQL Database**:
   - Click "New +" → "PostgreSQL"
   - Choose Free plan
   - Copy the **Internal Database URL**

4. **Set Environment Variables** (in Web Service settings):
   - `DATABASE_URL`: Paste PostgreSQL URL from step 3
   - `SECRET_KEY`: Run `python -c "import secrets; print(secrets.token_hex(32))"` to generate
   - `ADMIN_PASSWORD`: Your admin password
   - `FLASK_DEBUG`: `False`

5. **Deploy!** Your app will be live at `https://your-app.onrender.com`

**Note**: Free tier spins down after 15 min inactivity but wakes on request (first load may take 30-60 seconds).

### Alternative: Railway.app

1. Go to [railway.app](https://railway.app)
2. Click "New Project" → "Deploy from GitHub"
3. Add PostgreSQL database (automatic)
4. Set environment variables (same as above)
5. Deploy!

See `DEPLOYMENT.md` for detailed instructions and troubleshooting.

## Usage

1. **Add Members**: Navigate to "Add Member" page and add member names
2. **Track Meals**: Go to "Meals" page and select meal counts (0-5) for each member for each day
3. **Export PDF**: Click "Export PDF" to download monthly meal report
4. **Admin Access**: Click "Admin" and enter password to edit past meal records

## Admin Features

- View meal records for the past 7, 14, 30, or 60 days
- Edit existing meal records
- Create new meal records for past dates
- Only accessible with admin password

## Notes

- The meal tracking page shows 7 days starting from today
- Each day resets to 0/null values if no data is entered
- PDF export shows monthly totals for the current month
- All data is stored in PostgreSQL database

## License

This project is open source and available for personal use.
