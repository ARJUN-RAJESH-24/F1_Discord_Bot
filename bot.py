import os
import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv
import fastf1
from datetime import datetime, timedelta
import pytz
import pandas as pd
import json
import asyncio # For sleep

# Load environment variables
load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
try:
    GUILD_ID = int(os.getenv("GUILD_ID"))
except (ValueError, TypeError):
    print("Error: GUILD_ID not found or invalid in .env. Please ensure it's set correctly.")
    GUILD_ID = None 

# Define intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True 
intents.guilds = True 

bot = commands.Bot(command_prefix="!", intents=intents)

# Enable FastF1 caching for performance
fastf1.Cache.enable_cache('cache')

# Define the timezone for India (IST)
INDIAN_TIMEZONE = pytz.timezone('Asia/Kolkata')

reported_sessions = set()

F1_BOT_CHANNEL_ID = None 

# --- File for storing favorite drivers and their assigned role IDs ---
FAV_DRIVERS_FILE = 'data/fav_drivers.json'
fav_drivers_data = {} 
driver_roles_cache = {} 

def load_fav_drivers():
    global fav_drivers_data, driver_roles_cache
    if os.path.exists(FAV_DRIVERS_FILE):
        with open(FAV_DRIVERS_FILE, 'r') as f:
            try:
                loaded_data = json.load(f)
                fav_drivers_data = {int(k): v for k, v in loaded_data.get('users', {}).items()}
                driver_roles_cache = {k: int(v) for k, v in loaded_data.get('roles', {}).items()}
                print(f"Loaded favorite drivers data: {fav_drivers_data}")
                print(f"Loaded driver roles cache: {driver_roles_cache}")
            except json.JSONDecodeError as e:
                print(f"Error decoding fav_drivers.json: {e}. Starting with empty data.")
                fav_drivers_data = {}
                driver_roles_cache = {}
    else:
        print("No fav_drivers.json found, starting fresh.")

def save_fav_drivers():
    with open(FAV_DRIVERS_FILE, 'w') as f:
        data_to_save = {
            'users': {str(k): v for k, v in fav_drivers_data.items()},
            'roles': driver_roles_cache
        }
        json.dump(data_to_save, f, indent=4)
        print("Saved favorite drivers data.")


# --- Hardcoded Circuit Information (Can be expanded) ---
CIRCUIT_INFO = {
    "BAHRAIN": {
        "full_name": "Bahrain International Circuit",
        "location": "Sakhir, Bahrain",
        "lap_distance_km": 5.412,
        "turns": 15,
        "track_type": "Race Circuit, Permanent",
        "characteristics": "Medium-speed, technical, known for heavy braking zones. Medium downforce.",
        "home_team": "None (used for testing)"
    },
    "JEDDAH": {
        "full_name": "Jeddah Corniche Circuit",
        "location": "Jeddah, Saudi Arabia",
        "lap_distance_km": 6.174,
        "turns": 27,
        "track_type": "Street Circuit",
        "characteristics": "Fastest street circuit, high-speed corners, tight sections. Low-medium downforce.",
        "home_team": "None"
    },
    "MELBOURNE": {
        "full_name": "Albert Park Circuit",
        "location": "Melbourne, Australia",
        "lap_distance_km": 5.278,
        "turns": 14,
        "track_type": "Street Circuit, Semi-permanent",
        "characteristics": "Medium-speed, flowing, combination of fast and slow corners. Medium downforce.",
        "home_team": "None"
    },
    "SUZUKA": {
        "full_name": "Suzuka International Racing Course",
        "location": "Suzuka, Japan",
        "lap_distance_km": 5.807,
        "turns": 18,
        "track_type": "Race Circuit, Permanent",
        "characteristics": "High-speed, flowing, iconic S-curves, challenging. High downforce.",
        "home_team": "Honda (Engine supplier for Red Bull/RB)"
    },
    "SHANGHAI": {
        "full_name": "Shanghai International Circuit",
        "location": "Shanghai, China",
        "lap_distance_km": 5.451,
        "turns": 16,
        "track_type": "Race Circuit, Permanent",
        "characteristics": "Long straights, unique 'snail' turns, varied corner speeds. Medium downforce.",
        "home_team": "None"
    },
    "MIAMI": {
        "full_name": "Miami International Autodrome",
        "location": "Miami Gardens, Florida, USA",
        "lap_distance_km": 5.412,
        "turns": 19,
        "track_type": "Street Circuit, Temporary",
        "characteristics": "Mix of high-speed straights and slow technical sections. Medium downforce.",
        "home_team": "None"
    },
    "IMOLA": {
        "full_name": "Autodromo Enzo e Dino Ferrari",
        "location": "Imola, Italy",
        "lap_distance_km": 4.909,
        "turns": 19,
        "track_type": "Race Circuit, Permanent",
        "characteristics": "Classic, narrow, challenging, fast corners. High downforce.",
        "home_team": "Ferrari (nearby), RB (formerly AlphaTauri, nearby)"
    },
    "MONACO": {
        "full_name": "Circuit de Monaco",
        "location": "Monte Carlo, Monaco",
        "lap_distance_km": 3.337,
        "turns": 19,
        "track_type": "Street Circuit, Temporary",
        "characteristics": "Tight, twisty, low-speed, requires maximum downforce. High downforce.",
        "home_team": "None (but iconic for many drivers)"
    },
    "MONTREAL": {
        "full_name": "Circuit Gilles Villeneuve",
        "location": "Montreal, Canada",
        "lap_distance_km": 4.361,
        "turns": 14,
        "track_type": "Street Circuit, Semi-permanent",
        "characteristics": "High-speed sections, chicanes, 'Wall of Champions'. Low downforce.",
        "home_team": "None"
    },
    "BARCELONA": {
        "full_name": "Circuit de Barcelona-Catalunya",
        "location": "Montmeló, Spain",
        "lap_distance_km": 4.657,
        "turns": 14,
        "track_type": "Race Circuit, Permanent",
        "characteristics": "Mix of high, medium, and low-speed corners, good for testing. Medium-High downforce.",
        "home_team": "None (used heavily for testing by all teams)"
    },
    "SPIELBERG": {
        "full_name": "Red Bull Ring",
        "location": "Spielberg, Austria",
        "lap_distance_km": 4.318,
        "turns": 10,
        "track_type": "Race Circuit, Permanent",
        "characteristics": "Short, fast, high-altitude, steep inclines/declines. Medium-Low downforce.",
        "home_team": "Red Bull Racing (owned by Red Bull)"
    },
    "SILVERSTONE": {
        "full_name": "Silverstone Circuit",
        "location": "Silverstone, UK",
        "lap_distance_km": 5.891,
        "turns": 18,
        "track_type": "Race Circuit, Permanent",
        "characteristics": "High-speed, flowing, iconic corners like Copse, Maggotts, Becketts. High downforce.",
        "home_team": "Mercedes, Red Bull, Aston Martin, Alpine, Williams, McLaren (all based in UK)"
    },
    "HUNGARORING": {
        "full_name": "Hungaroring",
        "location": "Mogyoród, Hungary",
        "lap_distance_km": 4.381,
        "turns": 14,
        "track_type": "Race Circuit, Permanent",
        "characteristics": "Tight, twisty, often compared to a 'street circuit without walls'. High downforce.",
        "home_team": "None"
    },
    "SPA": {
        "full_name": "Circuit de Spa-Francorchamps",
        "location": "Stavelot, Belgium",
        "lap_distance_km": 7.004,
        "turns": 20,
        "track_type": "Race Circuit, Permanent",
        "characteristics": "Longest circuit, elevation changes, iconic Eau Rouge/Raidillon. Medium-low downforce.",
        "home_team": "None"
    },
    "ZANDVOORT": {
        "full_name": "Circuit Zandvoort",
        "location": "Zandvoort, Netherlands",
        "lap_distance_km": 4.259,
        "turns": 14,
        "track_type": "Race Circuit, Permanent",
        "characteristics": "Old-school, flowing, banked corners, narrow. High downforce.",
        "home_team": "None"
    },
    "MONZA": {
        "full_name": "Autodromo Nazionale Monza",
        "location": "Monza, Italy",
        "lap_distance_km": 5.793,
        "turns": 11,
        "track_type": "Race Circuit, Permanent",
        "characteristics": "Temple of Speed, long straights, heavy braking chicanes. Very low downforce.",
        "home_team": "Ferrari (nearby)"
    },
    "BAKU": {
        "full_name": "Baku City Circuit",
        "location": "Baku, Azerbaijan",
        "lap_distance_km": 6.003,
        "turns": 20,
        "track_type": "Street Circuit",
        "characteristics": "Longest straight, very narrow castle section. Low downforce.",
        "home_team": "None"
    },
    "SINGAPORE": {
        "full_name": "Marina Bay Street Circuit",
        "location": "Marina Bay, Singapore",
        "lap_distance_km": 4.940,
        "turns": 23,
        "track_type": "Street Circuit, Temporary",
        "characteristics": "Night race, humid, bumpy, physically demanding, lots of corners. High downforce.",
        "home_team": "None"
    },
    "AUSTIN": {
        "full_name": "Circuit of the Americas",
        "location": "Austin, Texas, USA",
        "lap_distance_km": 5.513,
        "turns": 20,
        "track_type": "Race Circuit, Permanent",
        "characteristics": "Elevation changes, mix of high-speed sweeps and tight hairpins. Medium-High downforce.",
        "home_team": "None"
    },
    "MEXICO": {
        "full_name": "Autódromo Hermanos Rodríguez",
        "location": "Mexico City, Mexico",
        "lap_distance_km": 4.304,
        "turns": 17,
        "track_type": "Race Circuit, Permanent",
        "characteristics": "High altitude, long straights, stadium section. High downforce (to compensate for thin air).",
        "home_team": "None"
    },
    "SAO_PAULO": {
        "full_name": "Autódromo José Carlos Pace (Interlagos)",
        "location": "São Paulo, Brazil",
        "lap_distance_km": 4.309,
        "turns": 15,
        "track_type": "Race Circuit, Permanent",
        "characteristics": "Anti-clockwise, undulating, challenging corners, enthusiastic crowd. Medium downforce.",
        "home_team": "None"
    },
    "LAS_VEGAS": {
        "full_name": "Las Vegas Strip Circuit",
        "location": "Las Vegas, Nevada, USA",
        "lap_distance_km": 6.201,
        "turns": 17,
        "track_type": "Street Circuit, Temporary",
        "characteristics": "Night race, extremely long straights, fast. Low downforce.",
        "home_team": "None"
    },
    "ABU_DHABI": {
        "full_name": "Yas Marina Circuit",
        "location": "Abu Dhabi, UAE",
        "lap_distance_km": 5.554,
        "turns": 16,
        "track_type": "Race Circuit, Permanent",
        "characteristics": "Modern, smooth, mix of slow and medium speed, changes for overtaking. Medium downforce.",
        "home_team": "None (used for end-of-season testing)"
    },
    "QATAR": {
        "full_name": "Lusail International Circuit",
        "location": "Lusail, Qatar",
        "lap_distance_km": 5.380,
        "turns": 16,
        "track_type": "Race Circuit, Permanent",
        "characteristics": "High-speed, flowing, challenging corners, often windy. Medium downforce.",
        "home_team": "None"
    }
}


# --- Custom Check Function for F1 Channel (for prefix commands) ---
def is_f1_channel():
    async def predicate(ctx):
        if F1_BOT_CHANNEL_ID is None:
            await ctx.send("The F1 bot channel has not been set yet. An admin can set it using `!setf1channel #channel-name`.", ephemeral=True)
            return False
        elif ctx.channel.id == F1_BOT_CHANNEL_ID:
            return True
        else:
            await ctx.send(f"Please use F1 commands in the designated F1 channel: <#{F1_BOT_CHANNEL_ID}>", delete_after=5)
            await ctx.message.delete(delay=3) 
            return False
    return commands.check(predicate)

# --- Event Handlers ---
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    print("------")
    await bot.change_presence(activity=discord.Game(name="Watching F1"))
    
    load_fav_drivers()

    if GUILD_ID: 
        try:
            await bot.tree.sync(guild=discord.Object(id=GUILD_ID))
            print(f"Synced slash commands for guild ID: {GUILD_ID}")
        except Exception as e:
            print(f"Failed to sync slash commands: {e}")
    else:
        print("GUILD_ID not set or invalid, skipping slash command sync.")

    check_for_completed_sessions.start()
    print("Started background task: check_for_completed_sessions")

@bot.event
async def on_disconnect():
    check_for_completed_sessions.cancel()
    print("Cancelled background task: check_for_completed_sessions")

# --- Prefix Commands ---

@bot.command(name="setf1channel", help="Sets the channel for F1 session updates and where F1 commands can be used.")
@commands.has_permissions(manage_channels=True)
async def set_f1_channel(ctx, channel_arg: str): # <--- FIX APPLIED HERE
    global F1_BOT_CHANNEL_ID

    if channel_arg.startswith('<#') and channel_arg.endswith('>'):
        try:
            channel_id = int(channel_arg[2:-1]) 
        except ValueError:
            await ctx.send("That doesn't look like a valid channel mention or ID. Please try mentioning the channel (e.g., `#f1-updates`) or providing its raw ID.")
            return
    else:
        try:
            channel_id = int(channel_arg)
        except ValueError:
            await ctx.send("That doesn't look like a valid channel ID. Please try mentioning the channel (e.g., `#f1-updates`) or providing its raw ID.")
            return

    channel = bot.get_channel(channel_id)
    if channel is None or not isinstance(channel, discord.TextChannel):
        await ctx.send(f"Could not find a text channel with ID {channel_id} or it's not a text channel. Please ensure I have access to it.")
        return

    F1_BOT_CHANNEL_ID = channel.id
    await ctx.send(f"F1 updates and commands will now be limited to {channel.mention}.")
    print(f"F1 bot channel set to: {channel.name} (ID: {channel.id})")


@bot.command(name="ping", help="Responds with Pong!")
@is_f1_channel() 
async def ping(ctx):
    await ctx.send("Pong!")

@bot.command(name="hello", help="Greets the user.")
@is_f1_channel() 
async def hello(ctx):
    await ctx.send(f"Hello, {ctx.author.display_name}!")

@bot.command(name="nextf1", help="Shows the schedule for the next F1 event in Indian time.")
@is_f1_channel() 
async def next_f1_event(ctx):
    await ctx.send("Fetching next F1 event schedule...")
    try:
        current_year = datetime.now().year
        schedule = fastf1.get_event_schedule(current_year, drop_duplicates=False)
        
        current_utc_time = datetime.now(pytz.utc) 
        
        upcoming_events = schedule[
            (schedule['EventDate'] >= current_utc_time.replace(hour=0, minute=0, second=0, microsecond=0)) &
            (schedule['RaceDate'] >= current_utc_time - timedelta(days=1)) 
        ]
        
        if upcoming_events.empty:
            await ctx.send("No upcoming F1 events found for the current season.")
            return

        upcoming_events = upcoming_events.sort_values(by='EventDate')
        next_event = upcoming_events.iloc[0]

        event_name = next_event['EventName']

        session_details = []
        session_types = ['Practice1Date', 'Practice2Date', 'Practice3Date', 'QualifyingDate', 'SprintQualifyingDate', 'SprintDate', 'RaceDate']
        
        for session_type_col in session_types:
            if session_type_col in next_event and pd.notna(next_event[session_type_col]):
                session_date_utc = next_event[session_type_col]
                if session_date_utc.tzinfo is None:
                    session_date_utc = pytz.utc.localize(session_date_utc)
                
                session_date_ist = session_date_utc.astimezone(INDIAN_TIMEZONE)
                
                session_name = session_type_col.replace('Date', '').replace('1', ' 1').replace('2', ' 2').replace('3', ' 3').replace('Qualifying', ' Qualifying').replace('SprintQualifying', ' Sprint Qualifying').replace('Sprint', ' Sprint').replace('Race', ' Race').strip()

                session_details.append(f"**{session_name}:** {session_date_ist.strftime('%d %b %Y, %I:%M %p IST')}")

        embed = discord.Embed(
            title=f"Next F1 Event: {event_name}",
            description="Here's the schedule for the upcoming F1 event (all times in Indian Standard Time (IST)):",
            color=0xFF0000
        )
        embed.add_field(name="Event Details", value="\n".join(session_details) if session_details else "No session details available.", inline=False)
        embed.set_footer(text="Data provided by FastF1")

        await ctx.send(embed=embed)

    except Exception as e:
        print(f"An error occurred in !nextf1: {e}")
        await ctx.send(f"Sorry, I couldn't fetch the F1 schedule right now. An error occurred: `{e}`")

# --- Slash Commands ---

@bot.tree.command( # Corrected to bot.tree.command
    name="setfavdriver", 
    description="Set your favorite F1 driver and get a fan role!",
    guild=discord.Object(id=GUILD_ID)
)
@discord.app_commands.describe(
    driver_code="The 3-letter code of your favorite driver (e.g., VER, HAM, LEC)"
)
async def set_fav_driver(interaction: discord.Interaction, driver_code: str):
    await interaction.response.defer(ephemeral=True) 

    driver_code = driver_code.upper() 
    user = interaction.user
    guild = interaction.guild

    driver_full_name = driver_code 
    
    try:
        current_year = datetime.now().year
        all_events = fastf1.get_event_schedule(current_year)
        
        all_driver_abbreviations = set()
        for _, event_data in all_events.iterrows():
            try:
                # Use 'Race' or 'Qualifying' as these generally have full driver lists
                session_type_to_load = 'Race' 
                if 'Qualifying' in event_data['Session1'] or 'Qualifying' in event_data['Session2'] or 'Qualifying' in event_data['Session3'] or 'Qualifying' in event_data['Session4'] or 'Qualifying' in event_data['Session5']:
                    session_type_to_load = 'Qualifying'
                elif 'Sprint' in event_data['Session1'] or 'Sprint' in event_data['Session2'] or 'Sprint' in event_data['Session3'] or 'Sprint' in event_data['Session4'] or 'Sprint' in event_data['Session5']:
                    session_type_to_load = 'Sprint'

                temp_session = fastf1.get_session(event_data.year, event_data.RoundNumber, session_type_to_load)
                
                # Check if session.drivers is available without full load, or load minimally
                if temp_session and hasattr(temp_session, 'drivers') and temp_session.drivers is not None:
                    for driver_info in temp_session.drivers.values():
                        all_driver_abbreviations.add(driver_info['Abbreviation'])
                        if driver_info['Abbreviation'] == driver_code:
                            driver_full_name = driver_info['FullName']
                else: # Fallback: if .drivers is None, try a minimal load
                     temp_session.load(laps=False, telemetry=False, weather=False)
                     if temp_session and hasattr(temp_session, 'drivers') and temp_session.drivers is not None:
                         for driver_info in temp_session.drivers.values():
                            all_driver_abbreviations.add(driver_info['Abbreviation'])
                            if driver_info['Abbreviation'] == driver_code:
                                driver_full_name = driver_info['FullName']

            except Exception:
                pass
        
        if driver_code not in all_driver_abbreviations:
            await interaction.followup.send(
                f"'{driver_code}' is not a valid 3-letter driver code for this season. Please check the official F1 driver codes (e.g., VER, HAM, LEC).",
                ephemeral=True
            )
            return
            
    except Exception as e:
        print(f"Error validating driver code with FastF1: {e}")
        await interaction.followup.send(
            f"Could not fully validate driver code with F1 data at this moment, but proceeding with '{driver_code}'.", ephemeral=True
        )


    # 2. Get/Create the role for the driver
    role_id_from_cache = driver_roles_cache.get(driver_code)
    role = guild.get_role(role_id_from_cache) if role_id_from_cache else None

    role_name_full = f"{driver_full_name} Fan" # Primary target role name
    role_name_code = f"{driver_code} Fan"     # Fallback role name

    if not role: 
        role = discord.utils.get(guild.roles, name=role_name_full)
    
    if not role and driver_full_name != driver_code: # Check for the simpler code-based role if full name role not found
         role = discord.utils.get(guild.roles, name=role_name_code)


    if not role: # If still no role found, create it
        try:
            # Prefer full name for creation
            role_name_to_create = role_name_full if driver_full_name != driver_code else role_name_code
            
            bot_member = guild.get_member(bot.user.id)
            bot_highest_role_pos = bot_member.top_role.position if bot_member else 0
            
            role = await guild.create_role(
                name=role_name_to_create, 
                permissions=discord.Permissions.none(), 
                hoist=True, 
                mentionable=False, 
                reason=f"Created role for {driver_code} fans by {user.name}"
            )
            try:
                target_pos = max(1, bot_highest_role_pos - 1) 
                await role.edit(position=target_pos)
            except Exception as e:
                print(f"Could not adjust role position for {role.name}: {e}")
                
            print(f"Created new role: {role.name} with ID {role.id}")
            driver_roles_cache[driver_code] = role.id 
            save_fav_drivers() 
        except discord.Forbidden:
            await interaction.followup.send(
                "I don't have permission to create roles. Please ask a server admin to give me 'Manage Roles' permission and ensure my role is higher than other roles.", 
                ephemeral=True
            )
            return
        except Exception as e:
            await interaction.followup.send(
                f"An unexpected error occurred while creating the role: `{e}`", 
                ephemeral=True
            )
            print(f"Error creating role: {e}")
            return
    else: 
        if driver_code not in driver_roles_cache or driver_roles_cache[driver_code] != role.id:
            driver_roles_cache[driver_code] = role.id
            save_fav_drivers()

    # 3. Remove old favorite driver role (if any)
    current_fav_info = fav_drivers_data.get(user.id)
    if current_fav_info and current_fav_info.get("role_id"):
        old_role_id = current_fav_info["role_id"]
        if old_role_id != role.id: 
            old_role = guild.get_role(old_role_id)
            if old_role and old_role in user.roles:
                try:
                    await user.remove_roles(old_role, reason="Changing favorite driver role")
                    print(f"Removed old role {old_role.name} from {user.name}")
                except discord.Forbidden:
                    print(f"Bot lacks permissions to remove role {old_role.name} from {user.name}")
                except Exception as e:
                    print(f"Error removing old role: {e}")

    # 4. Assign the new favorite driver role
    try:
        if role not in user.roles: 
            await user.add_roles(role, reason="Set favorite F1 driver")
            
            fav_drivers_data[user.id] = {
                "driver_code": driver_code,
                "role_id": role.id
            }
            save_fav_drivers() 

            await interaction.followup.send(
                f"You've successfully set your favorite driver to **{driver_full_name}**! You now have the {role.mention} role.",
                ephemeral=False
            )
            print(f"{user.name} set fav driver to {driver_code}")
        else:
            await interaction.followup.send(
                f"Your favorite driver is already set to **{driver_full_name}** ({role.mention}). No changes made.",
                ephemeral=True
            )

    except discord.Forbidden:
        await interaction.followup.send(
            "I don't have permission to assign roles. Please ask a server admin to give me 'Manage Roles' permission and ensure my role is higher than the roles I need to assign/remove.", 
            ephemeral=True
        )
    except Exception as e:
        await interaction.followup.send(
            f"An unexpected error occurred while assigning the role: `{e}`", 
            ephemeral=True
        )
        print(f"Error assigning role: {e}")


@bot.tree.command( # Corrected to bot.tree.command
    name="favdriver_win_check",
    description="Check if your favorite driver won the most recent F1 race.",
    guild=discord.Object(id=GUILD_ID)
)
async def favdriver_win_check(interaction: discord.Interaction):
    await interaction.response.defer() 

    user_id = interaction.user.id
    fav_info = fav_drivers_data.get(user_id)

    if not fav_info or not fav_info.get("driver_code"):
        await interaction.followup.send("You haven't set your favorite driver yet! Use `/setfavdriver <driver_code>` first.", ephemeral=True)
        return
    
    fav_driver_code = fav_info["driver_code"]
    
    try:
        current_year = datetime.now().year
        schedule = fastf1.get_event_schedule(current_year, drop_duplicates=False)
        
        current_utc_time = datetime.now(pytz.utc)
        completed_races = schedule[
            (schedule['RaceDate'] < current_utc_time) & (schedule['EventFormat'] != 'testing') 
        ].sort_values(by='RaceDate', ascending=False) 

        if completed_races.empty:
            await interaction.followup.send("No F1 races have concluded yet this season.", ephemeral=True)
            return
        
        latest_race_event = completed_races.iloc[0]
        event_name = latest_race_event['EventName']
        race_round = latest_race_event['RoundNumber']

        session = fastf1.get_session(current_year, race_round, 'Race')
        
        try:
            await interaction.followup.send(f"Checking results for the latest race: **{event_name}**...", ephemeral=True)
            await asyncio.sleep(2) 
            session.load() 
        except Exception as e:
            print(f"Error loading session for win check ({event_name} Round {race_round}): {e}")
            await interaction.followup.send(
                f"Could not fetch full results for the latest race ({event_name}) at this moment. Data might not be fully available yet. Please try again later.",
                ephemeral=True
            )
            return

        results = session.results 
        
        if results.empty:
            await interaction.followup.send(f"No results found for the latest race: **{event_name}**. Data might not be available yet.", ephemeral=True)
            return

        winner_entry = results[results['Position'] == 1].iloc[0]
        winner_driver_code = winner_entry['Abbreviation']
        winner_full_name = winner_entry['FullName']
        
        if winner_driver_code == fav_driver_code:
            race_date_utc = latest_race_event['RaceDate']
            race_date_ist = race_date_utc.astimezone(INDIAN_TIMEZONE)
            
            embed = discord.Embed(
                title=f"🎉 Congratulations! {winner_full_name} Won the {event_name}!",
                description=f"Your favorite driver, **{winner_full_name}**, won the last race!",
                color=0xF5F5DC 
            )
            embed.add_field(name="Race Date (IST)", value=race_date_ist.strftime('%d %b %Y'), inline=True)
            embed.add_field(name="Race Start Time (IST)", value=race_date_ist.strftime('%I:%M %p IST'), inline=True)
            
            embed.set_footer(text="Data provided by FastF1")
            await interaction.followup.send(embed=embed)
        else:
            await interaction.followup.send(f"Unfortunately, your favorite driver (**{fav_driver_code}**) did not win the last race (**{event_name}**). The winner was **{winner_full_name}**.", ephemeral=False)

    except Exception as e:
        print(f"An error occurred in /favdriver_win_check: {e}")
        await interaction.followup.send(f"Sorry, I couldn't check the race results right now. An error occurred: `{e}`", ephemeral=True)


@bot.tree.command( # Corrected to bot.tree.command
    name="upcomingraces",
    description="Shows the schedule for upcoming F1 races in Indian time.",
    guild=discord.Object(id=GUILD_ID)
)
async def upcoming_races(interaction: discord.Interaction):
    await interaction.response.defer()

    try:
        current_year = datetime.now().year
        schedule = fastf1.get_event_schedule(current_year, drop_duplicates=False)
        
        current_utc_time = datetime.now(pytz.utc) 
        
        upcoming_events = schedule[
            (schedule['RaceDate'] > current_utc_time) & (schedule['EventFormat'] != 'testing')
        ].sort_values(by='RaceDate') 
        
        if upcoming_events.empty:
            await interaction.followup.send("No upcoming F1 races found for the current season.")
            return

        embed = discord.Embed(
            title="🗓️ Upcoming F1 Race Calendar",
            description="Here's the schedule for the next few upcoming F1 Grand Prix weekends (all times in Indian Standard Time (IST)):",
            color=0xFF4500 
        )

        for i, event in upcoming_events.head(5).iterrows():
            event_name = event['EventName']
            race_date_utc = event['RaceDate'] 
            
            race_date_ist = race_date_utc.astimezone(INDIAN_TIMEZONE)
            
            event_start_date_ist = event['EventDate'].astimezone(INDIAN_TIMEZONE)
            
            value = (
                f"**Race Date:** {race_date_ist.strftime('%d %b %Y, %I:%M %p IST')}\n"
                f"**(Weekend Starts: {event_start_date_ist.strftime('%d %b %Y')})**"
            )
            embed.add_field(name=f"Round {event['RoundNumber']}: {event_name} ({event['Location']})", value=value, inline=False)
        
        embed.set_footer(text="Data provided by FastF1")
        await interaction.followup.send(embed=embed)

    except Exception as e:
        print(f"An error occurred in /upcomingraces: {e}")
        await interaction.followup.send(f"Sorry, I couldn't fetch the upcoming races right now. An error occurred: `{e}`", ephemeral=True)


@bot.tree.command( # Corrected to bot.tree.command
    name="circuitinfo",
    description="Get detailed information about an F1 circuit.",
    guild=discord.Object(id=GUILD_ID)
)
@discord.app_commands.describe(
    circuit_name="The name or common abbreviation of the circuit (e.g., Monza, Silverstone, Baku)"
)
async def circuit_info(interaction: discord.Interaction, circuit_name: str):
    await interaction.response.defer(ephemeral=True)

    search_term = circuit_name.upper().replace(" ", "_").replace("-", "_") 

    found_circuit_key = None
    for key, info in CIRCUIT_INFO.items():
        if search_term == key or \
           search_term in info['full_name'].upper().replace(" ", "_").replace("-", "_") or \
           search_term in info['location'].upper().replace(" ", "_").replace("-", "_"): 
            found_circuit_key = key
            break
    
    if found_circuit_key is None:
        await interaction.followup.send(f"Sorry, I couldn't find information for '{circuit_name}'. Please try a different name or abbreviation (e.g., 'Monza', 'Silverstone', 'Spa', 'Bahrain').", ephemeral=True)
        return

    circuit_data = CIRCUIT_INFO[found_circuit_key]

    embed = discord.Embed(
        title=f"🏎️ Circuit Info: {circuit_data['full_name']}",
        description=f"Details about the {circuit_data['full_name']} located in {circuit_data['location']}.",
        color=0x4169E1 
    )
    embed.add_field(name="📍 Location", value=circuit_data['location'], inline=True)
    embed.add_field(name="📏 Lap Distance", value=f"{circuit_data['lap_distance_km']} km", inline=True)
    embed.add_field(name="↩️ Number of Turns", value=circuit_data['turns'], inline=True)
    embed.add_field(name="🛣️ Track Type", value=circuit_data['track_type'], inline=False)
    embed.add_field(name="💨 Characteristics", value=circuit_data['characteristics'], inline=False)
    embed.add_field(name="🏠 Home of Team", value=circuit_data['home_team'], inline=False)

    embed.set_footer(text="Information from F1 Bot's knowledge base. Some characteristics are qualitative.")
    await interaction.followup.send(embed=embed)


# --- Background Task: Check for completed sessions ---
@tasks.loop(minutes=10)
async def check_for_completed_sessions():
    global F1_BOT_CHANNEL_ID 

    if F1_BOT_CHANNEL_ID is None:
        print("F1 bot channel not set. Skipping scheduled F1 updates.")
        return

    channel = bot.get_channel(F1_BOT_CHANNEL_ID)
    if channel is None:
        print(f"Could not find channel with ID {F1_BOT_CHANNEL_ID}. Please set a valid channel.")
        return

    print(f"Checking for completed F1 sessions at {datetime.now(INDIAN_TIMEZONE).strftime('%d %b %Y, %I:%M %p IST')}") 

    try:
        current_year = datetime.now().year
        
        schedule = pd.DataFrame()
        try:
            schedule = fastf1.get_event_schedule(current_year, drop_duplicates=False)
        except Exception as e:
            print(f"Could not fetch current year's schedule: {e}. Trying previous year or next year.")
            # Fallback to previous year if early in season and current year is empty
            if datetime.now().month <= 3: # If Q1, maybe try previous year
                try:
                    schedule = fastf1.get_event_schedule(current_year - 1, drop_duplicates=False)
                except Exception: pass
            if schedule.empty and datetime.now().month >= 10: # If late season and current is empty, try next year
                try:
                    schedule = fastf1.get_event_schedule(current_year + 1, drop_duplicates=False)
                except Exception: pass

            if schedule.empty:
                print("No F1 schedule could be loaded from current, previous, or next year. Skipping update check.")
                return 
            
        current_utc_time = datetime.now(pytz.utc)
        
        for _, event in schedule.iterrows():
            event_name = event['EventName']
            
            session_types_for_results = ['Practice1', 'Practice2', 'Practice3', 'Qualifying', 'SprintQualifying', 'Sprint', 'Race']

            for session_type_short in session_types_for_results:
                session_end_col = f'{session_type_short}EndDate' 
                session_start_col = f'{session_type_short}Date' 

                if session_start_col in event and pd.notna(event[session_start_col]):
                    session_start_time_utc = event[session_start_col]
                    session_end_time_utc = event[session_end_col] if session_end_col in event and pd.notna(event[session_end_col]) else session_start_time_utc + timedelta(hours=2) 

                    if session_start_time_utc.tzinfo is None:
                        session_start_time_utc = pytz.utc.localize(session_start_time_utc)
                    if session_end_time_utc.tzinfo is None:
                        session_end_time_utc = pytz.utc.localize(session_end_time_utc)
                    
                    session_identifier = f"{event.year}_{event.RoundNumber}_{session_type_short}" 

                    data_available_time = session_end_time_utc + timedelta(minutes=60) 

                    if current_utc_time >= data_available_time and session_identifier not in reported_sessions:
                        print(f"Detected completed and unreported session: {event_name} {session_type_short}")
                        
                        try:
                            session = fastf1.get_session(event.year, event.RoundNumber, session_type_short)
                            
                            await asyncio.sleep(5) 
                            
                            session.load(laps=True, telemetry=False, weather=False) 

                            if session.laps.empty:
                                print(f"No lap data available for {event_name} {session_type_short} yet after load. Will retry.")
                                continue

                            all_laps = session.laps.reset_index(drop=True)
                            
                            if 'IsAccurate' in all_laps.columns:
                                accurate_laps = all_laps[all_laps['IsAccurate'] == True]
                            else:
                                accurate_laps = all_laps 

                            fastest_laps = accurate_laps.pick_fastest()
                            
                            if fastest_laps.empty:
                                print(f"No fastest accurate lap data available for {event_name} {session_type_short}. Will retry.")
                                continue

                            top_3_drivers = fastest_laps.sort_values(by='LapTime').head(3)

                            embed = discord.Embed(
                                title=f"🏁 F1 Session Concluded: {event_name} - {session_type_short} Results",
                                description=f"Detailed results for the {event_name} {session_type_short} session.",
                                color=0x00FF00
                            )
                            embed.set_thumbnail(url="https://i.imgur.com/k6lP09a.png")

                            if session_type_short in ['Race', 'Sprint']:
                                session_results = session.results
                                if not session_results.empty and 1 in session_results['Position'].values:
                                    winner_driver = session_results[session_results['Position'] == 1].iloc[0]
                                    embed.add_field(name="🥇 Winner", value=f"{winner_driver['FullName']} ({winner_driver['Abbreviation']})", inline=False)
                                else:
                                    embed.add_field(name="🥇 Winner", value="Not available", inline=False)
                                
                                podium_text = []
                                for i, driver_row in session_results.head(3).iterrows(): 
                                    podium_text.append(f"P{int(driver_row['Position'])}: {driver_row['FullName']} ({driver_row['Abbreviation']})")
                                if podium_text:
                                    embed.add_field(name="🏆 Podium", value="\n".join(podium_text), inline=False)
                                else:
                                     embed.add_field(name="🏆 Podium", value="Not available", inline=False)
                                embed.add_field(name="\u200B", value="**Fastest Laps (Top 3 for detailed stats):**", inline=False) 

                            for i, (idx, driver_lap) in enumerate(top_3_drivers.iterrows()):
                                driver_code = driver_lap['Driver']
                                driver_name = session.get_driver(driver_code)['FullName']
                                lap_time = driver_lap['LapTime']
                                
                                lap_time_str = ""
                                if pd.notna(lap_time):
                                    total_seconds = int(lap_time.total_seconds())
                                    minutes = total_seconds // 60
                                    seconds = total_seconds % 60
                                    milliseconds = lap_time.microseconds // 1000
                                    lap_time_str = f"{minutes:02d}:{seconds:02d}.{milliseconds:03d}"
                                else:
                                    lap_time_str = "N/A"

                                sector1_time = driver_lap['Sector1Time']
                                sector2_time = driver_lap['Sector2Time']
                                sector3_time = driver_lap['Sector3Time']
                                tyre_compound = driver_lap['Compound']
                                tyre_age = driver_lap['TyreLife']

                                s1_str = f"{str(sector1_time)[7:12]}" if pd.notna(sector1_time) else "N/A"
                                s2_str = f"{str(sector2_time)[7:12]}" if pd.notna(sector2_time) else "N/A"
                                s3_str = f"{str(sector3_time)[7:12]}" if pd.notna(sector3_time) else "N/A"


                                field_value = (
                                    f"**Lap Time:** {lap_time_str}\n"
                                    f"**S1/S2/S3:** {s1_str} / {s2_str} / {s3_str}\n"
                                    f"**Tyre:** {tyre_compound} (Laps: {int(tyre_age) if pd.notna(tyre_age) else 'N/A'})"
                                )
                                embed.add_field(name=f"Fastest Lap - {driver_name} ({driver_code})", value=field_value, inline=False)
                            
                            embed.set_footer(text="Data provided by FastF1 | Fastest lap times shown.")
                            await channel.send(embed=embed)
                            
                            reported_sessions.add(session_identifier)

                        except Exception as e:
                            print(f"Error fetching/processing FastF1 data for {event_name} {session_type_short}: {e}")

    except Exception as e:
        print(f"An unexpected error occurred in check_for_completed_sessions: {e}")

# --- Run the bot ---
if DISCORD_TOKEN is not None:
    if GUILD_ID is None:
        print("Bot will start, but slash commands may not sync correctly without GUILD_ID. Please set GUILD_ID in your .env file.")
        bot.run(DISCORD_TOKEN)
    else:
        bot.run(DISCORD_TOKEN)
else:
    print("Error: DISCORD_TOKEN not found. Make sure it's set in your .env file.")