# keybr-bot
A bot for the keybr website

# To run this on a Raspberry Pi:

1. Install dependencies:
```zsh
pip install playwright
```

```zsh
python -m playwright install chromium
```
2. **Create Auth File:**
Run python `create_auth.py` on a machine with a display. Enter the login link from your email when prompted. This will create `auth_state.json`.
3. **Transfer Files:**
   Copy your `main.py` script and the generated auth_state.json file to your Raspberry Pi.
4. Schedule with Cron:
- Open the cron table for editing: `crontab -e`.
- Add a line to schedule your script. For example, to run it at 8:00 AM every day:
```zsh
0 8 * * * /usr/bin/python3 /path/to/your/main.py >> /path/to/your/cron.log 2>&1
```
Replace `/path/to/your/` with the actual paths on your Raspberry Pi. Redirecting output to a log file is useful for debugging.
cron entry to run at 08:00 every Workday:
```zsh
0 8 * * 1-5 /usr/bin/python3 /path/to/your/main.py >> /path/to/your/cron.log 2>&1
```
