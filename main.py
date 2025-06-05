import nextcord
from nextcord.ext import commands
from nextcord import SlashOption
import json
import os
import asyncio
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

# Bot configuration
DISCORD_TOKEN = "MTM4MDI2NTI4MjExNDk0OTE3MA.GVPjFF.79jzlqJw4WqIwOuLPjdn8Hobp8g6pY8RZXJkU0"
CHANNEL_ID = 1379286990477983795
ADMIN_IDS = [550322941250895882, 311036928910950401]

# Status emojis and their corresponding text
STATUS_EMOJIS = {
    'undetected': '🟢',
    'updating': '🔵',
    'high_risk': '🟠',
    'testing': '🟡',
    'detected': '🔴'
}

STATUS_CHOICES = [
    'undetected',
    'updating', 
    'high_risk',
    'testing',
    'detected'
]

# Initialize bot
intents = nextcord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

class GameStatusBot:
    def __init__(self):
        self.data_file = 'data/status.json'
        self.ensure_data_directory()
        
    def ensure_data_directory(self):
        if not os.path.exists('data'):
            os.makedirs('data')
            
    def load_data(self):
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                pass
        return {'games': {}, 'message_id': None}
    
    def save_data(self, data):
        with open(self.data_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def create_embed(self, games):
        embed = nextcord.Embed(
            title="STATUS OF PRODUCTS",
            description="View status for each product. Note that this is kept up to date by admins.",
            color=0x2F3136
        )
        
        if not games:
            embed.add_field(
                name="No Products Tracked", 
                value="Use `/addgame` to start tracking products", 
                inline=False
            )
        else:
            sorted_games = sorted(games.items())
            game_list = []
            for game_name, status in sorted_games:
                emoji = STATUS_EMOJIS.get(status, '⚪')
                status_text = status.replace('_', ' ').title()
                game_list.append(f"## {emoji} {game_name}")
                game_list.append(f"• {status_text}")
                game_list.append("")
            if game_list and game_list[-1] == "":
                game_list.pop()
            embed.description = '\n'.join(game_list)
        
        embed.set_footer(text="Last updated")
        embed.timestamp = nextcord.utils.utcnow()
        return embed
    
    async def update_status_board(self, channel, games, message_id=None):
        embed = self.create_embed(games)
        if message_id:
            try:
                message = await channel.fetch_message(message_id)
                await message.edit(embed=embed)
                return message_id
            except nextcord.NotFound:
                pass
        message = await channel.send(embed=embed)
        return message.id

game_handler = GameStatusBot()

def is_admin(interaction):
    return interaction.user.id in ADMIN_IDS

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    channel = bot.get_channel(CHANNEL_ID)
    if not channel:
        print(f"Error: Could not find channel with ID {CHANNEL_ID}")
        return
    data = game_handler.load_data()
    games = data.get('games', {})
    message_id = data.get('message_id')
    new_message_id = await game_handler.update_status_board(channel, games, message_id)
    if new_message_id != message_id:
        data['message_id'] = new_message_id
        game_handler.save_data(data)
    print(f"Status board ready in channel ID: {CHANNEL_ID}")

@bot.slash_command(name="addgame", description="Add a new game to track")
async def add_game(interaction: nextcord.Interaction, name: str = SlashOption(description="Game name to add"), status: str = SlashOption(description="Initial status", choices=STATUS_CHOICES)):
    if not is_admin(interaction):
        await interaction.response.send_message("❌ You don't have permission.", ephemeral=True)
        return
    data = game_handler.load_data()
    games = data.get('games', {})
    if name.lower() in [g.lower() for g in games.keys()]:
        await interaction.response.send_message(f"❌ Game '{name}' already exists.", ephemeral=True)
        return
    games[name] = status
    data['games'] = games
    game_handler.save_data(data)
    channel = bot.get_channel(CHANNEL_ID)
    if channel:
        message_id = await game_handler.update_status_board(channel, games, data.get('message_id'))
        data['message_id'] = message_id
        game_handler.save_data(data)
    await interaction.response.send_message(f"✅ Added '{name}' with status '{status.replace('_', ' ').title()}'", ephemeral=True)

@bot.slash_command(name="setstatus", description="Update the status of a game")
async def set_status(interaction: nextcord.Interaction, name: str = SlashOption(description="Game name to update"), status: str = SlashOption(description="New status", choices=STATUS_CHOICES)):
    if not is_admin(interaction):
        await interaction.response.send_message("❌ You don't have permission.", ephemeral=True)
        return
    data = game_handler.load_data()
    games = data.get('games', {})
    game_key = next((k for k in games if k.lower() == name.lower()), None)
    if not game_key:
        await interaction.response.send_message(f"❌ Game '{name}' not found.", ephemeral=True)
        return
    old_status = games[game_key].replace('_', ' ').title()
    games[game_key] = status
    data['games'] = games
    game_handler.save_data(data)
    channel = bot.get_channel(CHANNEL_ID)
    if channel:
        message_id = await game_handler.update_status_board(channel, games, data.get('message_id'))
        data['message_id'] = message_id
        game_handler.save_data(data)
    await interaction.response.send_message(f"✅ Updated '{game_key}' from '{old_status}' to '{status.replace('_', ' ').title()}'", ephemeral=True)

@bot.slash_command(name="listgames", description="Show all tracked games")
async def list_games(interaction: nextcord.Interaction):
    if not is_admin(interaction):
        await interaction.response.send_message("❌ You don't have permission.", ephemeral=True)
        return
    data = game_handler.load_data()
    games = data.get('games', {})
    if not games:
        await interaction.response.send_message("📋 No games being tracked.", ephemeral=True)
        return
    embed = nextcord.Embed(title="📋 Tracked Games", color=0x5865F2)
    game_list = [f"{STATUS_EMOJIS.get(status)} **{name}** - {status.replace('_', ' ').title()}" for name, status in sorted(games.items())]
    embed.add_field(name=f"Total Games: {len(games)}", value="\n".join(game_list), inline=False)
    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.slash_command(name="updatestatusboard", description="Refresh the status board manually")
async def update_status_board(interaction: nextcord.Interaction):
    if not is_admin(interaction):
        await interaction.response.send_message("❌ You don't have permission.", ephemeral=True)
        return
    data = game_handler.load_data()
    games = data.get('games', {})
    channel = bot.get_channel(CHANNEL_ID)
    if not channel:
        await interaction.response.send_message("❌ Channel not found.", ephemeral=True)
        return
    message_id = await game_handler.update_status_board(channel, games, data.get('message_id'))
    data['message_id'] = message_id
    game_handler.save_data(data)
    await interaction.response.send_message("✅ Status board updated.", ephemeral=True)

# Simple health check for Render hosting
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b'Bot is running!')
    def log_message(self, format, *args):
        pass

def start_health_server():
    port = int(os.environ.get('PORT', 10000))
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    server.serve_forever()

# Launch bot and health check
if __name__ == "__main__":
    if not DISCORD_TOKEN:
        print("Error: DISCORD_TOKEN is missing.")
        exit(1)
    threading.Thread(target=start_health_server, daemon=True).start()
    print("Starting bot...")
    bot.run(DISCORD_TOKEN)
