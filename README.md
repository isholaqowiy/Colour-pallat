# Colour Palette Extractor Telegram Bot

Extract dominant colours from any image with HEX, RGB, and HSL values.

## Features
- Extract 3, 6, 8, or 12 dominant colours
- Returns HEX, RGB, HSL values + % coverage
- Generates a visual palette swatch image
- Zero external API dependencies

## Local Setup
```bash
pip install -r requirements.txt
export BOT_TOKEN="your_telegram_bot_token"
python bot.py
```

## Deployment on Render.com

### Step 1 – Create Telegram Bot
1. Open Telegram, message `@BotFather`
2. Send `/newbot`, follow prompts, copy your **BOT_TOKEN**

### Step 2 – Push to GitHub
```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/colour-palette-bot.git
git push -u origin main
```

### Step 3 – Deploy on Render
1. Go to [render.com](https://render.com) → **New** → **Background Worker**
2. Connect GitHub and select your `colour-palette-bot` repo
3. Configure:
   - **Name:** `colour-palette-bot`
   - **Environment:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python bot.py`
4. Under **Environment Variables**, add:
   - Key: `BOT_TOKEN` → Value: *(your token)*
5. Click **Create Background Worker**

### Step 4 – Verify
- Send `/start` to your bot
- Send any photo
- Select number of colours
- Receive palette image + colour codes!
