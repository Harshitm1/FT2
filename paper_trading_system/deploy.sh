#!/bin/bash

# Quick deployment script for Railway
# This automates the GitHub push process

echo "======================================================================"
echo "🚀 RAILWAY DEPLOYMENT HELPER"
echo "======================================================================"
echo ""

# Check if git is initialized
if [ ! -d ".git" ]; then
    echo "📦 Initializing git repository..."
    git init
    echo "✅ Git initialized"
else
    echo "✅ Git already initialized"
fi

# Add all files
echo ""
echo "📝 Adding files to git..."
git add .

# Commit
echo ""
echo "💾 Creating commit..."
read -p "Enter commit message (or press Enter for default): " commit_msg
if [ -z "$commit_msg" ]; then
    commit_msg="Update paper trading system"
fi
git commit -m "$commit_msg"

# Check if remote exists
if git remote | grep -q "origin"; then
    echo ""
    echo "✅ Remote 'origin' already configured"
    echo "🚀 Pushing to GitHub..."
    git push origin main
else
    echo ""
    echo "⚠️  No remote repository configured"
    echo ""
    echo "Please create a GitHub repository and run:"
    echo "  git remote add origin https://github.com/YOUR_USERNAME/REPO_NAME.git"
    echo "  git branch -M main"
    echo "  git push -u origin main"
    echo ""
    echo "Then deploy on Railway:"
    echo "  1. Go to https://railway.app"
    echo "  2. Click 'New Project'"
    echo "  3. Select 'Deploy from GitHub repo'"
    echo "  4. Choose your repository"
fi

echo ""
echo "======================================================================"
echo "✅ DEPLOYMENT PREPARATION COMPLETE"
echo "======================================================================"
echo ""
echo "Next steps:"
echo "  1. Ensure code is pushed to GitHub"
echo "  2. Go to https://railway.app"
echo "  3. Deploy from your GitHub repository"
echo "  4. Monitor logs in Railway dashboard"
echo ""
