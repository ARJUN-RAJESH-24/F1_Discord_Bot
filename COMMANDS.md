# F1 Discord Bot - Comprehensive Commands Reference

## 🏎️ All Available Commands

### 📅 Race Schedule & Calendar

#### `/nextf1`

Get detailed schedule for the next F1 event with all session timings.

- **Example**: `/nextf1`
- **Output**: Weekend schedule with FP1, FP2, FP3, Qualifying, and Race times (IST)

#### `/upcomingraces`

View the next 5 upcoming Grand Prix weekends.

- **Example**: `/upcomingraces`
- **Output**: Race calendar with dates and locations

#### `/countdown`

⏱️ **NEW!** Live countdown to the very next F1 session.

- **Example**: `/countdown`
- **Output**: Days, hours, minutes remaining until next session

---

### 🔴 Live Session Features

#### `/livestatus`

🎯 **NEW!** Check current F1 session status with live flag updates.

- **Example**: `/livestatus`
- **Output**: Session state, track flags (🟢🟡🔴), safety car status, race control messages
- **When to use**: During race weekends to check track status

#### `/livetiming [driver_number]`

⚡ **NEW!** Get live lap times from the current session.

- **Example**: `/livetiming` or `/livetiming 1` (for Verstappen)
- **Output**: Most recent lap times for all drivers or specific driver
- **When to use**: During practice, qualifying, or race sessions

---

### 📊 Championship Standings

#### `/driverstandings [year]`

View driver championship standings (current or historical).

- **Example**: `/driverstandings` or `/driverstandings 2023`
- **Output**: Top 10 drivers with points, wins, and current team
- **Features**:
  - 🥇🥈🥉 Medal indicators for podium positions
  - Cached for fast loading (1 hour)

#### `/constructorstandings [year]`

View constructor/team championship standings.

- **Example**: `/constructorstandings` or `/constructorstandings 2022`
- **Output**: Top 10 teams with points and wins
- **Features**: Historical data back to 1950

---

### 🏁 Race Results

#### `/raceresults <race_name> [year]`

Get race results for any Grand Prix.

- **Example**: `/raceresults Monaco` or `/raceresults Silverstone 2023`
- **Output**: Top 10 finishers with times, teams, and points

#### `/detailedraceresults <race_name> [year]`

🎯 **NEW!** Enhanced race results with DNFs and fastest lap.

- **Example**: `/detailedraceresults Monaco`
- **Output**:
  - Top 10 finishers
  - ⚡ Fastest lap holder with time
  - ❌ DNFs with retirement reasons
- **Features**: Shows who had the fastest lap with lightning bolt indicator

#### `/qualifyingresults <race_name> [year]`

Get qualifying results with Q1/Q2/Q3 times.

- **Example**: `/qualifyingresults Monza` or `/qualifyingresults Spa 2023`
- **Output**: Top 10 qualifiers with all qualifying session times

---

### 👨‍✈️ Driver Information

#### `/driverprofile <driver_code>`

Get comprehensive career statistics for any F1 driver.

- **Example**: `/driverprofile verstappen` or `/driverprofile hamilton`
- **Output**:
  - 🏆 Championships
  - 🥇 Race wins
  - 🏅 Podiums
  - ⏱️ Pole positions
  - ⚡ Fastest laps
  - 💯 Career points
  - 🔗 Wikipedia link
- **Tip**: Use family name (verstappen, leclerc, alonso, etc.)

#### `/drivercomparison <driver1> <driver2>`

Compare two drivers head-to-head across their careers.

- **Example**: `/drivercomparison hamilton verstappen`
- **Output**: Side-by-side comparison of:
  - Championships
  - Race starts
  - Wins
  - Podiums
  - Poles
  - Fastest laps
  - Career points
- **Features**: Shows who's ahead in each category with 🏆

#### `/setfavdriver <driver_code>`

Set your favorite driver and get an exclusive fan role!

- **Example**: `/setfavdriver VER` or `/setfavdriver HAM`
- **Output**: Assigns you a role like "Max Verstappen Fan"
- **Features**:
  - Automatically creates role if it doesn't exist
  - Removes your old favorite driver role when you switch
  - Role displays on your server profile

#### `/favdriver_win_check`

Check if your favorite driver won the most recent race.

- **Example**: `/favdriver_win_check`
- **Output**: 🎉 Congratulations message if they won, or info about who did win
- **Requirement**: Must set favorite driver first with `/setfavdriver`

---

### 🏎️ Circuit & Track Information

#### `/circuitinfo <circuit_name>`

Get detailed information about any F1 circuit.

- **Example**: `/circuitinfo Monza` or `/circuitinfo Silverstone`
- **Output**:
  - 📍 Location
  - 📏 Lap distance (km)
  - ↩️ Number of turns
  - 🛣️ Track type (street circuit, permanent, etc.)
  - 💨 Characteristics (downforce level, track style)
  - 🏠 Home team (if applicable)
- **Supported circuits**: All 2024 F1 calendar circuits

---

### ⚙️ Admin Commands (Prefix-based)

#### `!setf1channel #channel-name`

Set the designated channel for F1 updates and where commands can be used.

- **Permission required**: Manage Channels
- **Example**: `!setf1channel #f1-updates`
- **Effect**:
  - All automated updates will post to this channel
  - Commands restricted to this channel (optional enforcement)

#### `!ping`

Check if bot is responsive.

- **Example**: `!ping`
- **Output**: `Pong!`

#### `!hello`

Get a friendly greeting.

- **Example**: `!hello`
- **Output**: `Hello, @YourName!`

---

## 📖 Usage Tips

### Quick Start

1. Use `/countdown` to see when the next session starts
2. During race weekend, use `/livestatus` to check flags and track conditions
3. After a race, use `/detailedraceresults <race>` for full recap

### Historical Data

- All commands with `[year]` parameter support historical queries back to 1950
- Example: `/driverstandings 1950` shows the very first F1 championship

### Live Features

- `/livestatus`, `/livetiming` only work during active race weekends
- Check during Practice, Qualifying, or Race sessions for live data
- Flag status updates: 🟢 Green, 🟡 Yellow, 🔴 Red, 🏁 Chequered, 🚗 Safety Car

### Best Practices

- **Before a race weekend**: `/countdown`, `/circuitinfo <track>`
- **During practice**: `/livetiming`, `/livestatus`
- **After qualifying**: `/qualifyingresults <race>`
- **After race**: `/detailedraceresults <race>`, `/driverstandings`
- **Off-season**: Explore historical data with year parameters

---

## 🎨 Features

### Rich Embeds

- Beautiful Discord embeds with colors and emojis
- Medal indicators (🥇🥈🥉) for podium positions
- Flag emojis for session status
- Lightning bolt (⚡) for fastest laps

### Smart Caching

- Standings cache: 1 hour
- Results cache: 24 hours
- Instant responses for cached queries

### Data Sources

- **Ergast API**: Historical data, standings, results (1950-present)
- **FastF1**: Session data, lap times, telemetry
- **OpenF1**: Live timing, track status, race control

---

## 🚨 Troubleshooting

**Slash commands not showing?**

- Wait 5 minutes after bot joins server
- Make sure bot has `applications.commands` scope
- Restart your Discord client

**"No data available" errors?**

- Check if you spelled the race/driver name correctly
- For historical data, ensure the year/race existed
- Live commands only work during active sessions

**Wrong timezone?**

- Bot currently displays times in IST (Indian Standard Time)
- Timezone customization coming soon!

---

## 📝 Command Summary Table

| Command | Type | Description | Example |
|---------|------|-------------|---------|
| `/countdown` | Schedule | Next session countdown | `/countdown` |
| `/nextf1` | Schedule | Next event details | `/nextf1` |
| `/upcomingraces` | Schedule | Upcoming calendar | `/upcomingraces` |
| `/livestatus` | Live | Track flags & status | `/livestatus` |
| `/livetiming` | Live | Live lap times | `/livetiming 44` |
| `/driverstandings` | Stats | Driver championship | `/driverstandings 2024` |
| `/constructorstandings` | Stats | Team championship | `/constructorstandings` |
| `/raceresults` | Results | Race finish order | `/raceresults Monaco` |
| `/detailedraceresults` | Results | Race + DNFs + fastest lap | `/detailedraceresults Spa` |
| `/qualifyingresults` | Results | Qualifying times | `/qualifyingresults Monza` |
| `/driverprofile` | Info | Career statistics | `/driverprofile leclerc` |
| `/drivercomparison` | Info | Head-to-head stats | `/drivercomparison alonso hamilton` |
| `/setfavdriver` | Community | Set favorite driver role | `/setfavdriver VER` |
| `/favdriver_win_check` | Community | Check if fav driver won | `/favdriver_win_check` |
| `/circuitinfo` | Info | Track details | `/circuitinfo Silverstone` |

---

**Total Commands**: 15 slash commands + 3 prefix commands

Need help? Check the main README or ask in your server's support channel!
