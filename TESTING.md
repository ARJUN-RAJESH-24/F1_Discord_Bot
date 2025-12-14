# Installation and Testing Guide

## Quick Start

### 1. Install Dependencies

Make sure you're in the F1DiscordBot directory and activate your virtual environment:

```bash
# Windows
venv\Scripts\activate

# Install all dependencies
pip install -r requirements.txt
```

### 2. Verify Installation

Run this command to check if all modules import correctly:

```bash
python -c "from api.ergast import ErgastAPI; from api.openf1 import OpenF1API; from utils.cache import cache; print('✅ All imports successful!')"
```

### 3. Test the Bot Locally

```bash
# Make sure .env file has your tokens
python bot.py
```

Expected output:

```
Logged in as YourBotName (ID: ...)
Synced slash commands for guild ID: ...
Started background task: check_for_completed_sessions
```

### 4. Test Commands in Discord

Try these commands in your Discord server:

- `/driverstandings` - Should show current F1 championship
- `/raceresults Monaco` - Should fetch Monaco GP results
- `/driverprofile verstappen` - Should show Max Verstappen's career stats

## Troubleshooting

### Import Errors

If you get `ModuleNotFoundError: No module named 'requests'`:

```bash
pip install -r requirements.txt
```

### Discord Token Issues

If bot doesn't start:

1. Check `.env` file exists
2. Verify `DISCORD_TOKEN` is correct
3. Verify `GUILD_ID` is your server ID

### Slash Commands Not Showing

1. Make sure bot has `applications.commands` scope
2. Wait 5 minutes after first sync
3. Try restarting Discord client

## Testing Checklist

- [ ] Bot starts without errors
- [ ] Slash commands appear in Discord
- [ ] `/driverstandings` works
- [ ] `/raceresults Monaco` returns data
- [ ] `/driverprofile verstappen` shows stats
- [ ] Cache directory is created after first API call
- [ ] Background task runs without errors

## Performance Testing

Check cache performance:

1. Run `/driverstandings` - Note the time
2. Run it again immediately - Should be instant (cached)
3. Check `cache/api_cache/` for cached files

## Railway Deployment Test

After deploying to Railway:

1. Check logs for "Logged in as..."
2. Test one slash command
3. Monitor for 24 hours to ensure it stays online
4. Check Railway metrics for resource usage

---

**Need Help?** Check the [README.md](file:///d:/Notes%20and%20Projects/Project/Bots/F1DiscordBot/README.md) for detailed setup instructions.
