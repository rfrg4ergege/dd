#!/usr/bin/env python3
"""
Sample script to populate the Discord bot with games from the screenshot
Run this after the bot is connected to add all the games shown in the UI
"""

import json
import os

def create_sample_data():
    """Create sample game data matching the screenshot"""
    
    # Ensure data directory exists
    if not os.path.exists('data'):
        os.makedirs('data')
    
    # Games from the screenshot with their statuses
    sample_games = {
        "Chevron EFT Cheat": "high_risk",
        "Kaffeine Valorant": "testing", 
        "Rust Private": "updating",
        "Crusader R6S Cheat": "undetected",
        "Temporary HWID Spoofer": "undetected",
        "Black Ops 6 External Cheat": "updating",
        "Zenith Black Ops 6 Cheat": "undetected",
        "Predator CS2": "undetected",
        "Counter Strike 2": "updating",
        "EFT Coffee Chams": "undetected",
        "Exception HWID Spoofer": "undetected",
        "EFT Coffee Lite": "undetected",
        "Exesense EFT Cheat": "undetected",
        "Warcraft War Thunder": "undetected",
        "Apex Legends External Cheat": "undetected",
        "Fortnite Private": "undetected",
        "Chevron DayZ Cheat": "undetected",
        "Valorant Safe Colorbot": "undetected",
        "Verse Permanent Spoofer": "undetected",
        "Predator Marvel Rivals Hack": "undetected"
    }
    
    # Create the data structure
    data = {
        'games': sample_games,
        'message_id': None  # Will be set when bot creates the message
    }
    
    # Save to JSON file
    with open('data/status.json', 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"Created sample data with {len(sample_games)} games")
    print("Restart the bot to load this data into the status board")

if __name__ == "__main__":
    create_sample_data()