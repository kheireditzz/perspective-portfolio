#!/data/data/com.termux/files/usr/bin/bash
cd /data/data/com.termux/files/home/perspective-portfolio

git add .
if git diff-index --quiet HEAD --; then
    echo "No changes to commit, pushing trigger..."
    git commit --allow-empty -m "update: trigger deploy via Telegram Bot CMS"
else
    git commit -m "update: content update via Telegram Bot CMS"
fi

git push origin main
PUSH_STATUS=$?

if [ $PUSH_STATUS -eq 0 ]; then
    echo "SUCCESS: Pushed to GitHub. Vercel is auto-building & deploying now!"
    exit 0
else
    echo "ERROR: Failed to push to GitHub."
    exit 1
fi
