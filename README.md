# Discord Game Status Tracker Bot

A full-featured Discord bot built with Python and nextcord that displays game status tracking in a clean UI format matching modern Discord themes. The bot posts a single embed message to track multiple games with color-coded status indicators.

## Features

- Clean game status tracking interface with dark theme design
- Real-time status updates via slash commands
- Persistent data storage with JSON
- Admin-only command restrictions
- Single embed message management
- Dropdown menus for better UX
- Auto-recovery on bot restart
- Sample data population script included

## Status Types

- 🟢 **Undetected** - Safe to use
- 🔵 **Updating** - Currently being updated
- 🟠 **High Risk** - Use with caution
- 🟡 **Testing** - Under testing
- 🔴 **Detected** - Not safe to use

## Available Commands

All commands are restricted to admin users only:

- `/addgame [name] [status]` - Add a new game to track
- `/setstatus [name] [status]` - Update the status of an existing game
- `/removegame [name]` - Remove a game from tracking
- `/updatestatusboard` - Manually refresh the embed
- `/listgames` - Show all current games and their statuses (ephemeral)

## Installation & Setup

### Prerequisites

- Python 3.8 or higher
- Discord Bot Token
- Discord server with appropriate permissions

### Step 1: Discord Bot Setup

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Create a new application and bot
3. Copy the bot token
4. Invite the bot to your server with these permissions:
   - Send Messages
   - Use Slash Commands
   - Embed Links
   - Read Message History
   - Manage Messages

### Step 2: Install Dependencies

```bash
pip install nextcord python-dotenv
```

### Step 3: Configuration

1. Create a `.env` file in the project directory:
   ```env
   DISCORD_TOKEN="your_bot_token_here"
   ```

2. Update configuration in `main.py` if needed:
   - `CHANNEL_ID`: Target channel ID (default: 1379286990477983795)
   - `ADMIN_IDS`: List of admin user IDs (default: [550322941250895882, 311036928910950401])

### Step 4: Running the Bot

```bash
python main.py
```

### Step 5: Populate Sample Data (Optional)

To quickly populate the bot with sample games matching the provided UI design:

```bash
python sample_games.py
```

Then restart the bot to load the new data.

## Project Structure

```
├── main.py              # Main bot application
├── sample_games.py      # Script to populate sample data
├── .env                 # Environment variables (create this)
├── .env.example         # Environment template
├── README.md            # This file
└── data/
    └── status.json      # Game status data (auto-created)
```

## Customization

### Changing Admin Users

Edit the `ADMIN_IDS` list in `main.py`:

```python
ADMIN_IDS = [your_user_id_1, your_user_id_2]
```

### Changing Target Channel

Update the `CHANNEL_ID` in `main.py`:

```python
CHANNEL_ID = your_channel_id_here
```

### Modifying Embed Design

The embed styling can be customized in the `create_embed()` method:

- Title and description
- Color scheme
- Game list formatting
- Footer text

## Troubleshooting

### Bot Not Connecting

1. Verify your Discord token is correct in `.env`
2. Check that the bot has necessary permissions
3. Ensure the bot is invited to your server

### Commands Not Working

1. Verify your user ID is in the `ADMIN_IDS` list
2. Check that slash commands are enabled for your server
3. Try using `/updatestatusboard` to refresh

### Status Board Not Updating

1. Verify the channel ID is correct
2. Check bot permissions in the target channel
3. Use `/updatestatusboard` to manually refresh

## Technical Details

- Built with `nextcord` (Discord API wrapper)
- Uses JSON for persistent data storage
- Implements slash commands with dropdown selections
- Auto-creates and manages single embed message
- Handles message recovery on bot restart

## License

This project is open source and available under standard terms.
