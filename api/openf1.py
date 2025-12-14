# OpenF1 API Client for Live F1 Data
# API Documentation: https://openf1.org/

import aiohttp
import asyncio
from typing import Optional, Dict, List
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

BASE_URL = "https://api.openf1.org/v1"

class OpenF1API:
    """Client for OpenF1 API - Live F1 Session Data"""
    
    def __init__(self):
        self.base_url = BASE_URL
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def _ensure_session(self):
        """Ensure aiohttp session exists"""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(headers={
                'User-Agent': 'F1DiscordBot/1.0'
            })
    
    async def _get(self, endpoint: str, params: Optional[Dict] = None) -> Optional[List[Dict]]:
        """Make an async GET request to the OpenF1 API"""
        await self._ensure_session()
        try:
            url = f"{self.base_url}/{endpoint}"
            async with self.session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=10)) as response:
                response.raise_for_status()
                return await response.json()
        except aiohttp.ClientError as e:
            logger.error(f"OpenF1 API request failed for {endpoint}: {e}")
            return None
        except asyncio.TimeoutError:
            logger.error(f"OpenF1 API timeout for {endpoint}")
            return None
    
    async def close(self):
        """Close the aiohttp session"""
        if self.session and not self.session.closed:
            await self.session.close()
    
    # === SESSION INFO ===
    
    async def get_latest_session(self) -> Optional[Dict]:
        """
        Get the most recent or current F1 session
        
        Returns:
            Latest session information
        """
        data = await self._get("sessions", params={'limit': 1})
        if data and len(data) > 0:
            return data[0]
        return None
    
    async def get_session_by_details(self, year: int, country: str, session_name: str) -> Optional[Dict]:
        """
        Get specific session by year, country, and session type
        
        Args:
            year: Season year
            country: Country name (e.g., 'Bahrain', 'Monaco')
            session_name: Session type ('Practice 1', 'Qualifying', 'Race', etc.)
        
        Returns:
            Session information
        """
        params = {
            'year': year,
            'country_name': country,
            'session_name': session_name
        }
        data = await self._get("sessions", params=params)
        if data and len(data) > 0:
            return data[0]
        return None
    
    # === LIVE TIMING ===
    
    async def get_lap_times(self, session_key: int, driver_number: Optional[int] = None) -> Optional[List[Dict]]:
        """
        Get lap times for a session
        
        Args:
            session_key: Session identifier from session info
            driver_number: Optional driver number to filter
        
        Returns:
            List of lap times
        """
        params = {'session_key': session_key}
        if driver_number:
            params['driver_number'] = driver_number
        
        return await self._get("laps", params=params)
    
    async def get_position_data(self, session_key: int, driver_number: Optional[int] = None) -> Optional[List[Dict]]:
        """
        Get position/location data during session
        
        Args:
            session_key: Session identifier
            driver_number: Optional driver number to filter
        
        Returns:
            Position data points
        """
        params = {'session_key': session_key}
        if driver_number:
            params['driver_number'] = driver_number
        
        return await self._get("position", params=params)
    
    # === DRIVER INFO ===
    
    async def get_drivers(self, session_key: Optional[int] = None) -> Optional[List[Dict]]:
        """
        Get driver information
        
        Args:
            session_key: Optional session to get drivers for
        
        Returns:
            List of drivers
        """
        params = {}
        if session_key:
            params['session_key'] = session_key
        
        return await self._get("drivers", params=params)
    
    # === TRACK STATUS / FLAGS ===
    
    async def get_track_status(self, session_key: int) -> Optional[List[Dict]]:
        """
        Get track status changes (flags, safety car, etc.)
        
        Args:
            session_key: Session identifier
        
        Returns:
            List of track status events
        """
        params = {'session_key': session_key}
        return await self._get("track_status", params=params)
    
    async def get_race_control_messages(self, session_key: int) -> Optional[List[Dict]]:
        """
        Get race control messages
        
        Args:
            session_key: Session identifier
        
        Returns:
            List of race control messages
        """
        params = {'session_key': session_key}
        return await self._get("race_control", params=params)
    
    # === TELEMETRY ===
    
    async def get_car_data(self, session_key: int, driver_number: int) -> Optional[List[Dict]]:
        """
        Get car telemetry data
        
        Args:
            session_key: Session identifier
            driver_number: Driver number
        
        Returns:
            Telemetry data (speed, RPM, gear, throttle, brake, DRS)
        """
        params = {
            'session_key': session_key,
            'driver_number': driver_number
        }
        return await self._get("car_data", params=params)
    
    # === STINTS ===
    
    async def get_stints(self, session_key: int, driver_number: Optional[int] = None) -> Optional[List[Dict]]:
        """
        Get tire stint information
        
        Args:
            session_key: Session identifier
            driver_number: Optional driver number to filter
        
        Returns:
            Stint data with compound and lap counts
        """
        params = {'session_key': session_key}
        if driver_number:
            params['driver_number'] = driver_number
        
        return await self._get("stints", params=params)
    
    # === HELPER FUNCTIONS ===
    
    async def is_session_live(self, session_key: int) -> bool:
        """
        Check if a session is currently live
        
        Args:
            session_key: Session identifier
        
        Returns:
            True if session is ongoing
        """
        # Get recent position data - if there's data from the last few minutes, session is likely live
        data = await self.get_position_data(session_key)
        if data and len(data) > 0:
            # Check if most recent data point is recent (within last 5 minutes)
            try:
                latest = data[-1]
                date_str = latest.get('date')
                if date_str:
                    latest_time = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                    now = datetime.now(latest_time.tzinfo)
                    delta = (now - latest_time).total_seconds()
                    return delta < 300  # Within 5 minutes
            except Exception as e:
                logger.error(f"Error checking if session is live: {e}")
        return False
    
    async def get_latest_track_status_message(self, session_key: int) -> Optional[str]:
        """
        Get the most recent track status
        
        Args:
            session_key: Session identifier
        
        Returns:
            Human-readable status message
        """
        statuses = await self.get_track_status(session_key)
        if statuses and len(statuses) > 0:
            latest = statuses[-1]
            status_code = latest.get('status')
            
            # Map status codes to messages
            status_map = {
                '1': '🟢 Track Clear',
                '2': '🟡 Yellow Flag',
                '3': '🟡 Double Yellow Flag',
                '4': '🟢 Green Flag',
                '5': '🔴 Red Flag',
                '6': '🟡 Virtual Safety Car Deployed',
                '7': '🟡 Virtual Safety Car Ending',
                '8': '🟡 Safety Car Deployed'
            }
            
            return status_map.get(str(status_code), f'Unknown Status: {status_code}')
        return None
