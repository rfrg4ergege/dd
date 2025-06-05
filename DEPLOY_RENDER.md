# Deploy Discord Bot to Render.com (Free Plan)

## Quick Setup Steps

### 1. Create Render Account
- Go to [render.com](https://render.com) and sign up for free
- Connect your GitHub account

### 2. Push Code to GitHub
- Create a new repository on GitHub
- Upload all these files to your repository

### 3. Deploy on Render
- In Render dashboard, click "New" → "Web Service"
- Connect your GitHub repository
- Use these settings:
  - **Environment**: Python 3
  - **Build Command**: `pip install -r requirements_render.txt`
  - **Start Command**: `python main.py`
  - **Plan**: Free

### 4. Add Environment Variable
- In your service settings, go to "Environment"
- Add environment variable:
  - **Key**: `DISCORD_TOKEN`
  - **Value**: Your Discord bot token

### 5. Update Channel ID
- Change line 14 in `main.py` to your Discord channel ID:
```python
CHANNEL_ID = YOUR_CHANNEL_ID_HERE
```

## Important Notes for Free Plan
- Free plan has 750 hours/month (enough for 24/7)
- Service sleeps after 15 minutes of inactivity
- First request after sleep takes ~30 seconds to wake up
- No persistent storage (games reset on restart)

## Files Included for Deployment
- `requirements_render.txt` - Python dependencies
- `render.yaml` - Render configuration
- `Procfile` - Process definition
- `start.sh` - Start script

Your bot will be ready once deployed!