#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 10 21:28:06 2020

@author: jasonkramer
"""

import json
import requests
from random import randint

leagueID = '591020442190389248'

def get_league_settings(leagueID):
    url = 'https://api.sleeper.app/v1/league/' + leagueID 
    r = requests.get(url)
    leagueSettings = r.json()
    if leagueSettings == None:
        return None
    return leagueSettings
    
def get_player_weekly_score(player, week, scoreSettings):
    #example: get_player_weekly_score('CHI', 1, scoreSettings)
    url = 'https://api.sleeper.app/stats/nfl/player/' + str(player) +'?season_type=regular&season=2020&grouping=week'
    r = requests.get(url)
    playerStats = r.json()
    if playerStats[str(week)]==None:
        return 0 #Maybe change to None so we know the difference?
        
    weeklyStats = playerStats[str(week)]["stats"]
    totalScore = 0
    for stat in weeklyStats:
        if stat in scoreSettings:
            totalScore += scoreSettings[stat]*weeklyStats[stat]
    totalScore = '%.2f'%(totalScore)
    print(float(totalScore))
    return float(totalScore)

def get_league_score_settings(leagueSettings):
    return leagueSettings["scoring_settings"]

def get_league_positions(leagueSettings):
    return leagueSettings["roster_positions"]

def get_team_amount(leagueSettings):
    return leagueSettings["settings"]["num_teams"]

def create_points_array(leagueSettings):
    positions = get_league_positions(leagueSettings)
    positions = [position for position in positions if position != 'BN']
    teamNum = get_team_amount(leagueSettings)
    positionNum = len(positions)
    
    arr =[[0]*positionNum for _ in range(teamNum)] 
    return arr

def get_unique_positions(leagueSettings):
    positions = get_league_positions(leagueSettings)
    positions = [position for position in positions if position != 'BN']
    positions = list(dict.fromkeys(positions))

    return positions

def calculate_week_scores(pointsArray, leagueID, scoreSettings, week):
    url = 'https://api.sleeper.app/v1/league/' + str(leagueID) + '/matchups/' + str(week)
    r = requests.get(url)
    teamRosters = r.json()
    
    for i, roster in enumerate(teamRosters):
        starters = roster['starters']
        for j, starter in enumerate(starters):
            pointsArray[i][j] = float('%.2f'%(pointsArray[i][j] + get_player_weekly_score(starter, week, scoreSettings)))

    return pointsArray

def calculate_total_scores(leaguePositions, leagueSettings, pointsArray):
    positions = get_league_positions(leagueSettings)
    positions = [position for position in positions if position != 'BN']
    uniquePositions = list(dict.fromkeys(positions))
    
    teamNum = get_team_amount(leagueSettings)
    positionNum = len(uniquePositions)

    cumulativeScore =[[0]*positionNum for _ in range(teamNum)] 

    for i, roster in enumerate(pointsArray):
        for j, spot in enumerate(roster):
            index = uniquePositions.index(positions[j])
            cumulativeScore[i][index] = float('%.2f'% (pointsArray[i][j] + cumulativeScore[i][index]))

    return cumulativeScore

def get_team_names(leagueID):
    url = 'https://api.sleeper.app/v1/league/' + leagueID + '/rosters/'
    r = requests.get(url)
    teamRosters = r.json()
    playerList = []
    for team in teamRosters:
        url = 'https://api.sleeper.app/v1/user/' + team["owner_id"]
        r = requests.get(url)
        player = r.json()
        playerList.append(player["username"])
        
    return playerList

leagueSettings = get_league_settings(leagueID)
scoreSettings = get_league_score_settings(leagueSettings)
leaguePositions = get_league_positions(leagueSettings)
pointsArray = create_points_array(leagueSettings)

for week in range(10): #1 + Current Week
    print(week)
    pointsArray = calculate_week_scores(pointsArray, leagueID, scoreSettings, week)
    print(pointsArray)
    
print(pointsArray)

week9scores = [[238.9, 119.5, 79.8, 129.9, 154.9, 83.6, 67.9, 82.7, 89.1, 194.1, 68.0, 54.0], [234.3, 102.1, 67.2, 71.2, 88.9, 57.4, 52.1, 40.0, 55.1, 80.6, 71.0, 84.0], [211.05, 99.0, 131.3, 106.7, 56.2, 79.6, 86.3, 99.0, 57.9, 127.15, 50.0, 81.0], [200.9, 96.5, 107.3, 123.6, 71.3, 52.9, 60.0, 43.8, 140.7, 189.6, 77.0, 62.0], [212.5, 161.7, 57.9, 125.3, 89.0, 82.1, 62.3, 73.1, 85.8, 184.25, 45.0, 69.0], [224.65, 124.9, 117.4, 153.8, 88.9, 64.2, 53.4, 60.3, 109.1, 218.5, 82.0, 54.0], [272.25, 147.3, 115.6, 126.6, 62.7, 76.7, 81.0, 47.9, 86.6, 175.1, 53.0, 60.0], [259.4, 80.3, 127.8, 64.4, 59.6, 98.5, 57.4, 108.3, 88.5, 275.15, 68.0, 60.0], [198.35, 102.7, 94.0, 45.6, 82.1, 53.5, 107.5, 76.7, 52.8, 222.2, 66.0, 78.0], [189.25, 132.8, 84.4, 100.1, 104.9, 47.1, 80.9, 86.9, 83.2, 132.85, 87.0, 84.0], [164.2, 79.8, 91.7, 47.9, 45.2, 74.1, 72.6, 106.4, 49.4, 69.85, 82.0, 37.0], [199.35, 93.7, 113.3, 108.3, 98.5, 90.1, 52.1, 93.8, 82.4, 155.6, 53.0, 43.0]]

totalScores = calculate_total_scores(leaguePositions, leagueSettings, pointsArray)
teamNames = get_team_names(leagueID)
uniquePositions = get_unique_positions(leagueSettings)
print("Generating position report...")
print('{:20}'.format("Player"), end = '')
for position in uniquePositions:
    print('{:12}'.format(position), end = '')

for i, score in enumerate(totalScores):
    print("\n")
    print('{:15}'.format(teamNames[i]), end = '')
    for position in score:
        print('{:12}'.format(position), end = '')

print("\n")
        


    



