import random
import chess.pgn
from urllib.request import urlopen
import os
import json
from pathlib import Path
from pgn_parser import pgn, parser
import json
import io
import datetime

SAVE_PATH = "C:/Chess/"
GAMES_PER_PLAYER = 5
PLAYERS_TO_COLLECT = 1000

players = json.load(urlopen(r"https://api.chess.com/pub/country/US/players"))["players"]
playersFile={}
gamesFolder = Path(f"{SAVE_PATH}/Dataset/Games")
playersFolder = Path(f"{SAVE_PATH}/Dataset/Players")

if not os.path.exists(gamesFolder):
    os.makedirs(gamesFolder)
if not os.path.exists(playersFolder):
    os.makedirs(playersFolder)
while len(players)>0 and PLAYERS_TO_COLLECT>0:
    i = random.randint(0,len(players))
    player = players[i]
    del players[i]
    PLAYERS_TO_COLLECT-=1
    archives = json.load(urlopen(rf"https://api.chess.com/pub/player/{player}/games/archives"))["archives"]
    for archive in archives:
        archiveString = f"Archive {archives.index(archive)}/{len(archives)}"
        games = json.load(urlopen(archive))["games"]
        for game in games:
            if(game["rated"]==False):
                continue
            try:
                pgnStr = game["pgn"]
            except Exception as e:
                print(f"Missing pgn file for {player} archive {archives.index(archive)} game {games.index(game)}, skipping game."+" "*10)
                continue    
            if "/daily/" in game["url"] or "/live/" not in game["url"] or game["rules"] != "chess" or game["rated"] != True:
                continue
            pgnObject = chess.pgn.read_game(io.StringIO(pgnStr))
            timeControl = pgnObject.headers["TimeControl"]
            baseTime=int(timeControl.split("+")[0])
            if not (600<=baseTime<=36000):
                continue
            if pgnObject.headers["Event"]!="Live Chess":
                continue

            whitePlayer = game["white"]["username"].lower()
            blackPlayer = game["black"]["username"].lower()

            if whitePlayer.lower() != player.lower() and whitePlayer.lower() not in players:
                players.append(whitePlayer.lower())
            if blackPlayer.lower() != player.lower() and blackPlayer.lower() not in players:
                players.append(blackPlayer.lower())

            StartYear,StartMonth,StartDay = pgnObject.headers["UTCDate"].split(".")
            StartHour,StartMinute,StartSecond = pgnObject.headers["UTCTime"].split(":")

            StartTime = int(datetime.datetime(int(StartYear),int(StartMonth),int(StartDay),int(StartHour),int(StartMinute),int(StartSecond),tzinfo=datetime.UTC).timestamp())

            if player.lower() == whitePlayer.lower():
                try:
                    playersFile[whitePlayer]
                except:
                    playersFile[whitePlayer]={}
                playersFile[whitePlayer][f"{game["url"].split("/")[-1]}"] = {"Side":"white", "ELO":game["white"]["rating"], "Outcome":game["white"]["result"], "OpponentResult":game["black"]["result"], "Opponent":blackPlayer, "OPPONENTELO":game["black"]["rating"], "STARTTIME":StartTime, "ENDTIME":game["end_time"]}
            elif player.lower() == blackPlayer.lower():
                try:
                    playersFile[blackPlayer]
                except:
                    playersFile[blackPlayer]={}
                playersFile[blackPlayer][f"{game["url"].split("/")[-1]}"] = {"Side":"black", "ELO":game["black"]["rating"], "Outcome":game["black"]["result"], "OpponentResult":game["white"]["result"],"Opponent":whitePlayer, "OPPONENTELO":game["white"]["rating"], "STARTTIME":StartTime, "ENDTIME":game["end_time"]}
                
            gameString = f"Game {games.index(game)}/{len(games)}"
            print(f"Downloading data for \"{player}\" ({i+1}/{len(players)}), {archiveString}, {gameString}"+" "*10, end="\r")
    with open(f"{SAVE_PATH}/players.json", 'w') as file:
        json_string = json.dumps(playersFile, default=lambda o: o.__dict__, sort_keys=True, indent=2)
        file.write(json_string)