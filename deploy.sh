#!/bin/bash
# Quick deployment script for Render/Railway

echo "🚀 Preparing for deployment..."

# Check if git is initialized
if [ ! -d ".git" ]; then
    echo "📦 Initializing git repository..."
    git init
    git add .
    git commit -m "Initial commit - Ready for deployment"
    echo "✅ Git initialized. Please add remote: git remote add origin YOUR_REPO_URL"
else
    echo "✅ Git repository found"
    git add .
    git commit -m "Update: Ready for deployment" || echo "No changes to commit"
fi

echo ""
echo "📋 Next steps:"
echo "1. Push to GitHub: git push -u origin main"
echo "2. Go to render.com or railway.app"
echo "3. Connect your repository"
echo "4. Set environment variables (see DEPLOYMENT.md)"
echo "5. Deploy!"
echo ""
echo "✨ Your app will be live 24/7!"
