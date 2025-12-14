# Ergast API Client for F1 Data
# API Documentation: http://ergast.com/mrd/

import requests
from typing import Optional, Dict, List
import logging

logger = logging.getLogger(__name__)

BASE_URL = "http://ergast.com/api/f1"

class ErgastAPI:
    """Client for the Ergast Developer API - Free F1 Historical Data"""
    
    def __init__(self):
        self.base_url = BASE_URL
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'F1DiscordBot/1.0'
        })
    
    def _get(self, endpoint: str, params: Optional[Dict] = None) -> Optional[Dict]:
        """Make a GET request to the Ergast API"""
        try:
            url = f"{self.base_url}/{endpoint}.json"
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Ergast API request failed for {endpoint}: {e}")
            return None
    
    # === STANDINGS ===
    
    def get_driver_standings(self, year: Optional[int] = None, round_num: Optional[int] = None) -> Optional[List[Dict]]:
        """
        Get driver championship standings
        
        Args:
            year: Season year (default: current)
            round_num: Round number (default: latest)
        
        Returns:
            List of driver standings with positions, points, wins, etc.
        """
        if year and round_num:
            endpoint = f"{year}/{round_num}/driverStandings"
        elif year:
            endpoint = f"{year}/driverStandings"
        else:
            endpoint = "current/driverStandings"
        
        data = self._get(endpoint)
        if data:
            try:
                standings_lists = data['MRData']['StandingsTable']['StandingsLists']
                if standings_lists:
                    return standings_lists[0]['DriverStandings']
            except (KeyError, IndexError) as e:
                logger.error(f"Error parsing driver standings: {e}")
        return None
    
    def get_constructor_standings(self, year: Optional[int] = None, round_num: Optional[int] = None) -> Optional[List[Dict]]:
        """
        Get constructor championship standings
        
        Args:
            year: Season year (default: current)
            round_num: Round number (default: latest)
        
        Returns:
            List of constructor standings with positions, points, wins, etc.
        """
        if year and round_num:
            endpoint = f"{year}/{round_num}/constructorStandings"
        elif year:
            endpoint = f"{year}/constructorStandings"
        else:
            endpoint = "current/constructorStandings"
        
        data = self._get(endpoint)
        if data:
            try:
                standings_lists = data['MRData']['StandingsTable']['StandingsLists']
                if standings_lists:
                    return standings_lists[0]['ConstructorStandings']
            except (KeyError, IndexError) as e:
                logger.error(f"Error parsing constructor standings: {e}")
        return None
    
    # === RACE RESULTS ===
    
    def get_race_results(self, year: int, round_num: int) -> Optional[Dict]:
        """
        Get race results for a specific Grand Prix
        
        Args:
            year: Season year
            round_num: Round number
        
        Returns:
            Race results with finishing positions, times, etc.
        """
        endpoint = f"{year}/{round_num}/results"
        data = self._get(endpoint)
        
        if data:
            try:
                races = data['MRData']['RaceTable']['Races']
                if races:
                    return races[0]
            except (KeyError, IndexError) as e:
                logger.error(f"Error parsing race results: {e}")
        return None
    
    def get_qualifying_results(self, year: int, round_num: int) -> Optional[Dict]:
        """
        Get qualifying results for a specific Grand Prix
        
        Args:
            year: Season year
            round_num: Round number
        
        Returns:
            Qualifying results with Q1, Q2, Q3 times
        """
        endpoint = f"{year}/{round_num}/qualifying"
        data = self._get(endpoint)
        
        if data:
            try:
                races = data['MRData']['RaceTable']['Races']
                if races:
                    return races[0]
            except (KeyError, IndexError) as e:
                logger.error(f"Error parsing qualifying results: {e}")
        return None
    
    # === SCHEDULE ===
    
    def get_race_schedule(self, year: Optional[int] = None) -> Optional[List[Dict]]:
        """
        Get race calendar/schedule
        
        Args:
            year: Season year (default: current)
        
        Returns:
            List of races with dates, circuit info, etc.
        """
        endpoint = f"{year}/races" if year else "current/races"
        data = self._get(endpoint)
        
        if data:
            try:
                return data['MRData']['RaceTable']['Races']
            except KeyError as e:
                logger.error(f"Error parsing race schedule: {e}")
        return None
    
    # === DRIVER INFO ===
    
    def get_driver_info(self, driver_id: str) -> Optional[Dict]:
        """
        Get detailed driver information
        
        Args:
            driver_id: Driver ID (e.g., 'max_verstappen', 'hamilton')
        
        Returns:
            Driver details
        """
        endpoint = f"drivers/{driver_id}"
        data = self._get(endpoint)
        
        if data:
            try:
                drivers = data['MRData']['DriverTable']['Drivers']
                if drivers:
                    return drivers[0]
            except (KeyError, IndexError) as e:
                logger.error(f"Error parsing driver info: {e}")
        return None
    
    def get_driver_career_stats(self, driver_id: str) -> Optional[Dict]:
        """
        Get comprehensive career statistics for a driver
        
        Args:
            driver_id: Driver ID
        
        Returns:
            Career stats including wins, podiums, poles, championships
        """
        # Get all race results for the driver
        endpoint = f"drivers/{driver_id}/results"
        params = {'limit': '1000'}  # Get all results
        data = self._get(endpoint, params)
        
        if not data:
            return None
        
        try:
            races = data['MRData']['RaceTable']['Races']
            
            # Calculate statistics
            stats = {
                'races': len(races),
                'wins': 0,
                'podiums': 0,
                'poles': 0,
                'fastest_laps': 0,
                'points': 0,
                'championships': 0
            }
            
            for race in races:
                if 'Results' in race and race['Results']:
                    result = race['Results'][0]
                    position = result.get('position', '999')
                    
                    if position == '1':
                        stats['wins'] += 1
                    if position in ['1', '2', '3']:
                        stats['podiums'] += 1
                    if result.get('grid') == '1':
                        stats['poles'] += 1
                    if result.get('rank') == '1':  # Fastest lap rank
                        stats['fastest_laps'] += 1
                    
                    points_str = result.get('points', '0')
                    try:
                        stats['points'] += float(points_str)
                    except ValueError:
                        pass
            
            # Get championships
            championships_data = self._get(f"drivers/{driver_id}/driverStandings/1", {'limit': '100'})
            if championships_data:
                standings_lists = championships_data['MRData']['StandingsTable']['StandingsLists']
                stats['championships'] = len(standings_lists)
            
            return stats
            
        except (KeyError, IndexError) as e:
            logger.error(f"Error calculating driver stats: {e}")
            return None
    
    # === CONSTRUCTOR INFO ===
    
    def get_constructor_info(self, constructor_id: str) -> Optional[Dict]:
        """
        Get detailed constructor/team information
        
        Args:
            constructor_id: Constructor ID (e.g., 'red_bull', 'ferrari')
        
        Returns:
            Constructor details
        """
        endpoint = f"constructors/{constructor_id}"
        data = self._get(endpoint)
        
        if data:
            try:
                constructors = data['MRData']['ConstructorTable']['Constructors']
                if constructors:
                    return constructors[0]
            except (KeyError, IndexError) as e:
                logger.error(f"Error parsing constructor info: {e}")
        return None
    
    # === FASTEST LAPS ===
    
    def get_fastest_laps(self, year: int, round_num: int) -> Optional[List[Dict]]:
        """
        Get fastest lap information for a race
        
        Args:
            year: Season year
            round_num: Round number
        
        Returns:
            List of drivers with fastest laps
        """
        endpoint = f"{year}/{round_num}/fastest/1/results"
        data = self._get(endpoint)
        
        if data:
            try:
                races = data['MRData']['RaceTable']['Races']
                if races and 'Results' in races[0]:
                    return races[0]['Results']
            except (KeyError, IndexError) as e:
                logger.error(f"Error parsing fastest laps: {e}")
        return None
    
    # === HELPER FUNCTIONS ===
    
    def search_driver_by_code(self, driver_code: str, year: Optional[int] = None) -> Optional[str]:
        """
        Find driver ID from 3-letter code
        
        Args:
            driver_code: 3-letter driver code (e.g., 'VER', 'HAM')
            year: Season year to search in
        
        Returns:
            Driver ID if found
        """
        endpoint = f"{year}/drivers" if year else "current/drivers"
        data = self._get(endpoint)
        
        if data:
            try:
                drivers = data['MRData']['DriverTable']['Drivers']
                for driver in drivers:
                    # Ergast doesn't have 3-letter codes, need to match by name
                    # This is a limitation - FastF1 is better for this
                    if driver['code'] == driver_code:
                        return driver['driverId']
            except KeyError as e:
                logger.error(f"Error searching for driver: {e}")
        return None
    
    def get_race_by_name(self, race_name: str, year: Optional[int] = None) -> Optional[int]:
        """
        Find round number by race name
        
        Args:
            race_name: Partial race name (e.g., 'Monaco', 'Silverstone')
            year: Season year
        
        Returns:
            Round number if found
        """
        schedule = self.get_race_schedule(year)
        if schedule:
            race_name_lower = race_name.lower()
            for race in schedule:
                circuit_name = race.get('Circuit', {}).get('circuitName', '').lower()
                race_full_name = race.get('raceName', '').lower()
                
                if race_name_lower in circuit_name or race_name_lower in race_full_name:
                    return int(race['round'])
        return None
