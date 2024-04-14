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

SAVE_PATH = "F:"
GAMES_PER_PLAYER = 5
PLAYERS_TO_COLLECT = 1000

# Get list of first 10,000 US players, sorted alphabetically
players = json.load(urlopen(r"https://api.chess.com/pub/country/US/players"))["players"]
playersFile={}
    
while len(players)>0 and PLAYERS_TO_COLLECT>0:
    # Select up to PLAYERS_TO_COLLECT random players.
    i = random.randint(0,len(players))
    player = players[i]
    del players[i]
    PLAYERS_TO_COLLECT-=1
    #Get list of archives from chess.com api
    archives = json.load(urlopen(rf"https://api.chess.com/pub/player/{player}/games/archives"))["archives"]
    for archive in archives:
        archiveString = f"Archive {archives.index(archive)}/{len(archives)}" # Read archive
        games = json.load(urlopen(archive))["games"]
        for game in games:
            try:
                pgnStr = game["pgn"]
            except Exception as e: #Skip games without pgn files
                print(f"Missing pgn file for {player} archive {archives.index(archive)} game {games.index(game)}, skipping game."+" "*10)
                continue    
            if "/daily/" in game["url"] or "/live/" not in game["url"] or game["rules"] != "chess" or game["rated"] != True: #Skip games that aren't live, are a different mode than regular chess, or aren't rated.
                continue
            if game["time_class"] != "rapid": #Skip games not classified as rapid (bullet and blitz has an outsize time pressure impact on gameplay), and longer than rapid is rarely played in live online. 
                continue
            pgnObject = chess.pgn.read_game(io.StringIO(pgnStr))
            if pgnObject.headers["Event"]!="Live Chess": #Skip daily games, and only do live games
                continue
            try:
                ECO=pgnObject.headers["ECO"] #Skip games without an ECO (these are games that were abandoned and resigned before real play started, because of an accidental start or something)
            except:
                continue

            whitePlayer = game["white"]["username"].lower()
            blackPlayer = game["black"]["username"].lower()

            #Add player to players list
            if whitePlayer.lower() != player.lower() and whitePlayer.lower() not in players:
                players.append(whitePlayer.lower())
            if blackPlayer.lower() != player.lower() and blackPlayer.lower() not in players:
                players.append(blackPlayer.lower())

            #Convert PGN start time into unix timestamp
            StartYear,StartMonth,StartDay = pgnObject.headers["UTCDate"].split(".")
            StartHour,StartMinute,StartSecond = pgnObject.headers["UTCTime"].split(":")
            StartTime = int(datetime.datetime(int(StartYear),int(StartMonth),int(StartDay),int(StartHour),int(StartMinute),int(StartSecond),tzinfo=datetime.UTC).timestamp())

            #Convert pgn into list of moves for each player, and remaining time at the end of each moves.
            moves = []
            mainline = pgnObject.mainline()
            for move in mainline:
                moves.append({"move":str(move.move),"clock":move.clock()})
            whiteMoves=[]
            blackMoves=[]
            for i in range(len(moves)):
                if i%2==0:
                    whiteMoves.append(moves[i])
                else:
                    blackMoves.append(moves[i])
            
            #Write game to player's file
            if player.lower() == whitePlayer.lower():
                try:
                    playersFile[whitePlayer]
                except:
                    playersFile[whitePlayer]={}
                playersFile[whitePlayer][f"{game["url"].split("/")[-1]}"] = {
                    "Side":"white",
                    "ELO":game["white"]["rating"], 
                    "Outcome":game["white"]["result"], 
                    "OpponentResult":game["black"]["result"], 
                    "Opponent":blackPlayer, 
                    "OpponentELO":game["black"]["rating"], 
                    "StartTime":StartTime, 
                    "EndTime":game["end_time"],
                    "TimeControl":game["time_control"],
                    "Termination":pgnObject.headers["Termination"],
                    "ECO":pgnObject.headers["ECO"],
                    "Round":pgnObject.headers["Round"],
                    "PlayerMoves":whiteMoves,
                    "OpponentMoves":blackMoves
                    }
            elif player.lower() == blackPlayer.lower():
                try:
                    playersFile[blackPlayer]
                except:
                    playersFile[blackPlayer]={}
                playersFile[blackPlayer][f"{game["url"].split("/")[-1]}"] = {
                    "Side":"black",
                    "ELO":game["black"]["rating"],
                    "Outcome":game["black"]["result"],
                    "OpponentResult":game["white"]["result"],
                    "Opponent":whitePlayer, 
                    "OpponentELO":game["white"]["rating"],
                    "StartTime":StartTime, 
                    "EndTime":game["end_time"],
                    "TimeControl":game["time_control"],
                    "Termination":pgnObject.headers["Termination"],
                    "ECO":pgnObject.headers["ECO"],
                    "Round":pgnObject.headers["Round"],
                    "Moves":moves,
                    "PlayerMoves":blackMoves,
                    "OpponentMoves":whiteMoves
                    }
            #Print status to console window    
            gameString = f"Game {games.index(game)}/{len(games)}"
            print(f"Downloading data for \"{player}\" ({i+1}/{len(players)}), {archiveString}, {gameString}"+" "*10, end="\r")
    
    # Write output file
    with open(f"{SAVE_PATH}/dataset.json", 'w') as file:
        json_string = json.dumps(playersFile, default=lambda o: o.__dict__, sort_keys=True, indent=2)
        file.write(json_string)