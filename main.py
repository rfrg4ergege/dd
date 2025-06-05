import nextcord
from nextcord.ext import commands
from nextcord import SlashOption
import json
import os
import asyncio
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Bot configuration
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
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
        """Create data directory if it doesn't exist"""
        if not os.path.exists('data'):
            os.makedirs('data')
            
    def load_data(self):
        """Load game data from JSON file"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                pass
        return {'games': {}, 'message_id': None}
    
    def save_data(self, data):
        """Save game data to JSON file"""
        with open(self.data_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def create_embed(self, games):
        """Create the status board embed"""
        embed = nextcord.Embed(
            title="STATUS OF PRODUCTS",
            description="View status for each product. Note that this is kept up to date by admins.",
            color=0x2F3136  # Dark theme color to match Discord's dark mode
        )
        
        if not games:
            embed.add_field(
                name="No Products Tracked", 
                value="Use `/addgame` to start tracking products", 
                inline=False
            )
        else:
            # Sort games alphabetically
            sorted_games = sorted(games.items())
            
            game_list = []
            for game_name, status in sorted_games:
                emoji = STATUS_EMOJIS.get(status, '⚪')
                status_text = status.replace('_', ' ').title()
                # Create clean format matching the new screenshot with larger circles and bullet points
                game_list.append(f"## {emoji} {game_name}")
                game_list.append(f"• {status_text}")
                game_list.append("")  # Empty line for spacing
            
            # Remove the last empty line
            if game_list and game_list[-1] == "":
                game_list.pop()
            
            embed.description = '\n'.join(game_list) if game_list else "No products tracked yet."
        
        embed.set_footer(text="Last updated")
        embed.timestamp = nextcord.utils.utcnow()
        
        return embed
    
    async def update_status_board(self, channel, games, message_id=None):
        """Update or create the status board message"""
        embed = self.create_embed(games)
        
        if message_id:
            try:
                message = await channel.fetch_message(message_id)
                await message.edit(embed=embed)
                return message_id
            except nextcord.NotFound:
                # Message was deleted, create a new one
                pass
        
        # Create new message
        message = await channel.send(embed=embed)
        return message.id

# Initialize the game status handler
game_handler = GameStatusBot()

def is_admin(interaction):
    """Check if user is an admin"""
    return interaction.user.id in ADMIN_IDS

@bot.event
async def on_ready():
    """Bot startup event"""
    print(f'{bot.user} has connected to Discord!')
    
    # Get the target channel
    channel = bot.get_channel(CHANNEL_ID)
    if not channel:
        print(f"Error: Could not find channel with ID {CHANNEL_ID}")
        return
    
    # Load existing data
    data = game_handler.load_data()
    games = data.get('games', {})
    message_id = data.get('message_id')
    
    # Update or create the status board
    new_message_id = await game_handler.update_status_board(channel, games, message_id)
    
    # Save the message ID if it changed
    if new_message_id != message_id:
        data['message_id'] = new_message_id
        game_handler.save_data(data)
    
    print(f"Status board ready in channel ID: {CHANNEL_ID}")

@bot.slash_command(name="addgame", description="Add a new game to track")
async def add_game(
    interaction: nextcord.Interaction,
    name: str = SlashOption(description="Game name to add"),
    status: str = SlashOption(description="Initial status", choices=STATUS_CHOICES)
):
    """Add a new game to the status tracker"""
    if not is_admin(interaction):
        await interaction.response.send_message("❌ You don't have permission to use this command.", ephemeral=True)
        return
    
    # Load current data
    data = game_handler.load_data()
    games = data.get('games', {})
    
    # Check if game already exists
    if name.lower() in [g.lower() for g in games.keys()]:
        await interaction.response.send_message(f"❌ Game '{name}' already exists. Use `/setstatus` to update it.", ephemeral=True)
        return
    
    # Add the game
    games[name] = status
    data['games'] = games
    game_handler.save_data(data)
    
    # Update the status board
    channel = bot.get_channel(CHANNEL_ID)
    if channel:
        message_id = await game_handler.update_status_board(channel, games, data.get('message_id'))
        data['message_id'] = message_id
        game_handler.save_data(data)
    
    status_text = status.replace('_', ' ').title()
    await interaction.response.send_message(f"✅ Added '{name}' with status '{status_text}'", ephemeral=True)

@bot.slash_command(name="setstatus", description="Update the status of a game")
async def set_status(
    interaction: nextcord.Interaction,
    name: str = SlashOption(description="Game name to update"),
    status: str = SlashOption(description="New status", choices=STATUS_CHOICES)
):
    """Update the status of an existing game"""
    if not is_admin(interaction):
        await interaction.response.send_message("❌ You don't have permission to use this command.", ephemeral=True)
        return
    
    # Load current data
    data = game_handler.load_data()
    games = data.get('games', {})
    
    # Find the game (case-insensitive)
    game_key = None
    for key in games.keys():
        if key.lower() == name.lower():
            game_key = key
            break
    
    if not game_key:
        await interaction.response.send_message(f"❌ Game '{name}' not found. Use `/listgames` to see all games.", ephemeral=True)
        return
    
    # Update the status
    old_status = games[game_key].replace('_', ' ').title()
    games[game_key] = status
    data['games'] = games
    game_handler.save_data(data)
    
    # Update the status board
    channel = bot.get_channel(CHANNEL_ID)
    if channel:
        message_id = await game_handler.update_status_board(channel, games, data.get('message_id'))
        data['message_id'] = message_id
        game_handler.save_data(data)
    
    new_status = status.replace('_', ' ').title()
    await interaction.response.send_message(f"✅ Updated '{game_key}' from '{old_status}' to '{new_status}'", ephemeral=True)

class RemoveGameView(nextcord.ui.View):
    def __init__(self, games_dict):
        super().__init__(timeout=60)
        self.games_dict = games_dict
        self.add_item(RemoveGameSelect(games_dict))

class RemoveGameSelect(nextcord.ui.Select):
    def __init__(self, games_dict):
        self.games_dict = games_dict
        
        # Create options for each game
        options = []
        for game_name, status in sorted(games_dict.items()):
            emoji = STATUS_EMOJIS.get(status, '⚪')
            status_text = status.replace('_', ' ').title()
            options.append(nextcord.SelectOption(
                label=game_name,
                description=f"Status: {status_text}",
                emoji=emoji,
                value=game_name
            ))
        
        super().__init__(
            placeholder="Choose games to remove...",
            min_values=1,
            max_values=min(len(options), 25),  # Discord limit is 25
            options=options
        )
    
    async def callback(self, interaction: nextcord.Interaction):
        # Load current data
        data = game_handler.load_data()
        games = data.get('games', {})
        
        removed_games = []
        for game_name in self.values:
            if game_name in games:
                del games[game_name]
                removed_games.append(game_name)
        
        # Save updated data
        data['games'] = games
        game_handler.save_data(data)
        
        # Update the status board
        channel = interaction.guild.get_channel(CHANNEL_ID)
        if channel:
            message_id = await game_handler.update_status_board(channel, games, data.get('message_id'))
            data['message_id'] = message_id
            game_handler.save_data(data)
        
        if removed_games:
            removed_list = "', '".join(removed_games)
            if len(removed_games) == 1:
                message = f"✅ Removed '{removed_list}' from tracking"
            else:
                message = f"✅ Removed {len(removed_games)} games: '{removed_list}'"
        else:
            message = "❌ No games were removed"
        
        await interaction.response.edit_message(content=message, view=None)

@bot.slash_command(name="removegame", description="Remove games from tracking")
async def remove_game(interaction: nextcord.Interaction):
    """Remove games from the status tracker using a selection menu"""
    if not is_admin(interaction):
        await interaction.response.send_message("❌ You don't have permission to use this command.", ephemeral=True)
        return
    
    # Load current data
    data = game_handler.load_data()
    games = data.get('games', {})
    
    if not games:
        await interaction.response.send_message("❌ No games are currently being tracked. Use `/addgame` to add some first.", ephemeral=True)
        return
    
    # Create the selection view
    view = RemoveGameView(games)
    
    embed = nextcord.Embed(
        title="🗑️ Remove Games",
        description="Select one or more games to remove from tracking:",
        color=0xFF6B6B
    )
    
    await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

@bot.slash_command(name="updatestatusboard", description="Manually refresh the status board")
async def update_status_board(interaction: nextcord.Interaction):
    """Manually update the status board"""
    if not is_admin(interaction):
        await interaction.response.send_message("❌ You don't have permission to use this command.", ephemeral=True)
        return
    
    # Load current data
    data = game_handler.load_data()
    games = data.get('games', {})
    
    # Update the status board
    channel = bot.get_channel(CHANNEL_ID)
    if not channel:
        await interaction.response.send_message("❌ Could not find the target channel.", ephemeral=True)
        return
    
    message_id = await game_handler.update_status_board(channel, games, data.get('message_id'))
    data['message_id'] = message_id
    game_handler.save_data(data)
    
    await interaction.response.send_message("✅ Status board updated successfully", ephemeral=True)

@bot.slash_command(name="listgames", description="Show all current games and their statuses")
async def list_games(interaction: nextcord.Interaction):
    """List all tracked games and their statuses"""
    if not is_admin(interaction):
        await interaction.response.send_message("❌ You don't have permission to use this command.", ephemeral=True)
        return
    
    # Load current data
    data = game_handler.load_data()
    games = data.get('games', {})
    
    if not games:
        await interaction.response.send_message("📋 No games are currently being tracked.", ephemeral=True)
        return
    
    # Create embed for the game list
    embed = nextcord.Embed(
        title="📋 All Tracked Games",
        color=0x5865F2
    )
    
    # Sort games alphabetically
    sorted_games = sorted(games.items())
    
    game_list = []
    for game_name, status in sorted_games:
        emoji = STATUS_EMOJIS.get(status, '⚪')
        status_text = status.replace('_', ' ').title()
        game_list.append(f"{emoji} **{game_name}** - {status_text}")
    
    embed.add_field(
        name=f"Total Games: {len(games)}", 
        value='\n'.join(game_list), 
        inline=False
    )
    
    await interaction.response.send_message(embed=embed, ephemeral=True)

# Error handling
@bot.event
async def on_application_command_error(interaction: nextcord.Interaction, error):
    """Handle command errors"""
    print(f"An error occurred: {error}")
    
    # Only respond if we haven't already responded to this interaction
    if not interaction.response.is_done():
        if isinstance(error, commands.MissingPermissions):
            await interaction.response.send_message("❌ You don't have permission to use this command.", ephemeral=True)
        else:
            await interaction.response.send_message("❌ An error occurred while processing your command.", ephemeral=True)

# Run the bot
if __name__ == "__main__":
    if not DISCORD_TOKEN:
        print("Error: DISCORD_TOKEN not found in environment variables")
        print("Please create a .env file with your bot token")
        exit(1)
    
    bot.run(DISCORD_TOKEN)
