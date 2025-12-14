# F1 Team Colors for Rich Embeds (2024 Season)

TEAM_COLORS = {
    # Current F1 Teams (2024)
    "RED BULL RACING": {
        "primary": 0x3671C6,  # Dark Blue
        "secondary": 0xFFD700,  # Gold
        "emoji": "🔵"
    },
    "FERRARI": {
        "primary": 0xE8002D,  # Ferrari Red
        "secondary": 0xFFFFFF,  # White
        "emoji": "🔴"
    },
    "MERCEDES": {
        "primary": 0x27F4D2,  # Turquoise
        "secondary": 0x000000,  # Black
        "emoji": "🩵"
    },
    "MCLAREN": {
        "primary": 0xFF8000,  # Papaya Orange
        "secondary": 0x47C7FC,  # Blue
        "emoji": "🧡"
    },
    "ASTON MARTIN": {
        "primary": 0x00665F,  # British Racing Green
        "secondary": 0xCEDB00,  # Lime
        "emoji": "🟢"
    },
    "ALPINE": {
        "primary": 0x0090FF,  # Alpine Blue
        "secondary": 0xFF1E00,  # Red
        "emoji": "💙"
    },
    "WILLIAMS": {
        "primary": 0x64C4FF,  # Light Blue
        "secondary": 0x041E42,  # Navy
        "emoji": "🔷"
    },
    "RB": {  # AlphaTauri/RB
        "primary": 0x6692FF,  # Blue
        "secondary": 0x1E3A5F,  # Dark Blue
        "emoji": "🦅"
    },
    "KICK SAUBER": {
        "primary": 0x00E701,  # Green
        "secondary": 0x000000,  # Black
        "emoji": "💚"
    },
    "HAAS": {
        "primary": 0xB6BABD,  # Silver
        "secondary": 0xED1C24,  # Red
        "emoji": "⚪"
    },
    
    # Legacy/Historical Teams
    "ALFA ROMEO": {
        "primary": 0xC92D4B,  # Burgundy Red
        "secondary": 0xFFFFFF,
        "emoji": "🔴"
    },
    "ALPHATAURI": {
        "primary": 0x4E7C9B,  # Blue
        "secondary": 0xFFFFFF,
        "emoji": "🔵"
    },
    "RACING POINT": {
        "primary": 0xF596C8,  # Pink
        "secondary": 0x000000,
        "emoji": "💗"
    },
    "RENAULT": {
        "primary": 0xFFF500,  # Yellow
        "secondary": 0x000000,
        "emoji": "💛"
    }
}

# Driver Number Colors (for personalization)
DRIVER_COLORS = {
    1: 0x3671C6,   # Verstappen - Red Bull Blue
    11: 0x3671C6,  # Perez - Red Bull Blue
    16: 0xE8002D,  # Leclerc - Ferrari Red
    55: 0xE8002D,  # Sainz - Ferrari Red
    44: 0x27F4D2,  # Hamilton - Mercedes Turquoise
    63: 0x27F4D2,  # Russell - Mercedes Turquoise
    4: 0xFF8000,   # Norris - McLaren Papaya
    81: 0xFF8000,  # Piastri - McLaren Papaya
    14: 0x00665F,  # Alonso - Aston Martin Green
    18: 0x00665F,  # Stroll - Aston Martin Green
    10: 0x0093CC,  # Gasly - Alpine Blue
    31: 0x0093CC,  # Ocon - Alpine Blue
    23: 0x64C4FF,  # Albon - Williams Blue
    2: 0x64C4FF,   # Sargeant - Williams Blue
    22: 0x6692FF,  # Tsunoda - RB Blue
    3: 0x6692FF,   # Ricciardo - RB Blue
    24: 0x00E701,  # Zhou - Sauber Green
    77: 0xB6BABD,  # Bottas - Sauber
    20: 0xB6BABD,  # Magnussen - Haas Silver
    27: 0xB6BABD,  # Hulkenberg - Haas Silver
}

def get_team_color(team_name: str) -> int:
    """
    Get primary color for a team
    
    Args:
        team_name: Team name (case-insensitive)
    
    Returns:
        Hex color code for discord embeds
    """
    team_upper = team_name.upper()
    
    # Try exact match first
    if team_upper in TEAM_COLORS:
        return TEAM_COLORS[team_upper]["primary"]
    
    # Try partial match
    for team_key in TEAM_COLORS:
        if team_key in team_upper or team_upper in team_key:
            return TEAM_COLORS[team_key]["primary"]
    
    # Default F1 red
    return 0xFF0000

def get_team_emoji(team_name: str) -> str:
    """Get emoji for a team"""
    team_upper = team_name.upper()
    
    for team_key in TEAM_COLORS:
        if team_key in team_upper or team_upper in team_key:
            return TEAM_COLORS[team_key]["emoji"]
    
    return "🏎️"

def get_driver_color(driver_number: int) -> int:
    """Get color for a driver by their number"""
    return DRIVER_COLORS.get(driver_number, 0xFF0000)

# Nationality Flag Emojis
NATIONALITY_FLAGS = {
    "DUTCH": "🇳🇱",
    "MEXICAN": "🇲🇽",
    "MONEGASQUE": "🇲🇨",
    "SPANISH": "🇪🇸",
    "BRITISH": "🇬🇧",
    "AUSTRALIAN": "🇦🇺",
    "FRENCH": "🇫🇷",
    "CANADIAN": "🇨🇦",
    "THAI": "🇹🇭",
    "JAPANESE": "🇯🇵",
    "AMERICAN": "🇺🇸",
    "CHINESE": "🇨🇳",
    "FINNISH": "🇫🇮",
    "DANISH": "🇩🇰",
    "GERMAN": "🇩🇪",
    "ITALIAN": "🇮🇹",
    "BRAZILIAN": "🇧🇷",
    "NEW ZEALANDER": "🇳🇿",
    "POLISH": "🇵🇱",
}

def get_nationality_flag(nationality: str) -> str:
    """Get flag emoji for nationality"""
    return NATIONALITY_FLAGS.get(nationality.upper(), "🏁")
