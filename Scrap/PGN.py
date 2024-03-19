import datetime

class PGN:
    @classmethod
    def fromFile(self, path:str):
        with open(path) as f:
            self=PGN(f.read())
    def __init__(self, content:str):
        self.str=content
        for line in content.split("\n"):
            if len(line)=="":
                continue

            if not "[" in line:
                pass

            line.removeprefix("[")
            line.removesuffix("]")
            if " " in line:
                lineAr=line.split(" ")
                match lineAr[0]:
                    case "Event":
                        self.Event = lineAr[1]
                    case "Site":
                        self.Site = lineAr[1]
                    case "Date":
                        dateAr=lineAr.split(".")
                        self.Date = datetime.datetime(int(dateAr[0]),int(dateAr[1]),int(dateAr[2]))
                    case "Round":
                        self.Round = lineAr[1]
                    case "White":
                        self.WhitePlayer = lineAr[1]
                    case "Black":
                        self.BlackPlayer = lineAr[1]
                    case "Result":
                        match lineAr[1]:
                            case "1-0":
                                self.Winner="White"
                            case "0-1":
                                self.Winner="Black"
                            case "1-1":
                                self.Winner="Draw"
                    case "CurentPosition":
                        self.EndPos = lineAr[1]
                    case "Timezone":
                        self.Timezone = lineAr[1]
                    case "ECO":
                        self.ECO=lineAr[1]
                    case "ECOUrl":
                        self.ECOUrl=lineAr[1]
                    case "UTCDate":
                        self.UTCDate=lineAr[1]
                    case "UTCTime":
                        self.UTCTime=lineAr[1]
                    case "WhiteElo":
                        self.WhiteElo=int(lineAr[1])
                    case "BlackElo":
                        self.BlackElo=int(lineAr[1])
                    case "TimeControl":
                        if("+" in lineAr[1]):
                            timeCntrlAr=lineAr[1].split("+")
                            self.Time=int(timeCntrlAr[0])
                            self.Increment=int(timeCntrlAr[1])
                        else:
                            self.Time=lineAr[1]
                    case "Termination":
                        if "timeout":
                            self.End="Timeout vs Insufficient Material"
                        elif "time" in lineAr[1]:
                            self.End="Time"
                        elif "resignation" in lineAr[1]:
                            self.End="Resign"
                        elif "checkmate" in lineAr[1]:
                            self.End="Checkmate"
                        elif "abandon" in lineAr[1]:
                            self.End="Abandonment"
                        elif "insufficient" in lineAr[1]:
                            self.End="Insufficient Material"
                        elif "repetition" in lineAr[1]:
                            self.End="Repetition"
                        elif "50" in lineAr[1]:
                            self.End="50 Move Rule"
                        elif "stalemate" in lineAr[1]:
                            self.End="Stalemate"
                    case "StartTime":
                        timeAr=lineAr[1].split(":")
                        self.StartTime=datetime.time(int(timeAr[0]),int(timeAr[1]),int(timeAr[2]))
                    case "EndTime":
                        timeAr=lineAr[1].split(":")
                        self.EndTime=datetime.time(int(timeAr[0]),int(timeAr[1]),int(timeAr[2]))
                    case "Link":
                        self.Link=lineAr[1]