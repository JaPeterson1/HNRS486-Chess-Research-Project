from math import fabs
from urllib.request import urlopen
import os
import json
from pathlib import Path
import secrets

SAVE_PATH = "F:"
GAMES_PER_PLAYER = 5

players = json.load(urlopen(r"https://api.chess.com/pub/country/US/players"))["players"]

gamesFolder = Path(f"{SAVE_PATH}/Dateset/Games")
playersFolder = Path(f"{SAVE_PATH}/Dateset/Players")

if not os.path.exists(gamesFolder):
    os.makedirs(gamesFolder)
if not os.path.exists(playersFolder):
    os.makedirs(playersFolder)
for i in range(len(players)):
    player = players[i]
    archives = json.load(urlopen(rf"https://api.chess.com/pub/player/{player}/games/archives"))["archives"]
    playerGames = []
    for archive in archives:
        archiveString = f"Archive {archives.index(archive)}/{len(archives)}"
        games = json.load(urlopen(archive))["games"]
        for game in games:
            whitePlayer = game["white"]["username"]
            blackPlayer = game["black"]["username"]
            if whitePlayer is not player and whitePlayer not in players:
                players.append(whitePlayer)
            if blackPlayer is not player and blackPlayer not in players:
                players.append(blackPlayer)
            gameString = f"Game {games.index(game)}/{len(games)}"
            print(f"Downloading data for \"{player}\" ({i+1}/{len(players)}), {archiveString}, {gameString}"+" "*10, end="\r")
            try:
                pgn = game["pgn"]
            except Exception as e:
                print(f"Missing pgn file for {player} archive {archives.index(archive)} game {games.index(game)}, skipping game."+" "*10)
                continue    
            if "/daily/" in game["url"] or "/live/" not in game["url"] or game["rules"] != "chess" or game["rated"] != True:
                continue
            playerGames.append(game)
    print(f"Writing game files for {player}..."+" "*10, end="\r")
    
    playerFile=[]
    for game in playerGames:
        playerFile.append(f"{game["url"].split("/")[-1]}")

    for game in secrets.choices(playerGames, k=GAMES_PER_PLAYER):
        with open(gamesFolder / f"{game["url"].split("/")[-1]}.pgn", "w+") as f:
            f.write(u""+pgn)
            f.close()