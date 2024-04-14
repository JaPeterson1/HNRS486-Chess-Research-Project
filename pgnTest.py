import chess
import chess.pgn

with open("349110516.pgn") as pgn:
    game = chess.pgn.read_game(pgn)

    moves = []
    mainline = game.mainline()
    for move in mainline:
        moves.append({"move":move.move,"clock":move.clock()})
            
    whiteMoves=[]
    blackMoves=[]
    for i in range(len(moves)):
        if i%2==0:
            whiteMoves.append(moves[i])
        else:
            blackMoves.append(moves[i])
            
import os
os.system("pause")