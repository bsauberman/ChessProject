"""
Stores all info about current state of chess game and determining the valid moves
at current state.
Also keeps move log
"""


class GameState():
    def __init__(self):
        # board is 8x8 2d list each element of the list has 2 characters
        # first character represents color (b or w)
        # second character represents the type of piece K Q R B N p
        # "--" represents empty space wth no piece
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"], ]

        self.moveFunctions = {'p': self.getPawnMoves, 'R': self.getRookMoves, 'N': self.getKnightMoves,
                              'B': self.getBishopMoves,
                              'Q': self.getQueenMoves, 'K': self.getKingMoves}
        self.enemyPiece = {True: 'b', False: 'w'}

        self.whiteToMove = True
        self.moveLog = []

        self.wKingLoc = (7, 4)
        self.bKingLoc = (0, 4)

        self.checkmate = False
        self.stalemate = False

        self.enpessantPossible = () #coordinates for the square where en pessant capture is possible
        self.currentCastlingRight = CastleRights(True, True, True, True)
        self.castleRightsLog = [CastleRights(self.currentCastlingRight.wks, self.currentCastlingRight.bks,
                                             self.currentCastlingRight.wqs, self.currentCastlingRight.bqs)]

    '''
    Takes move as a parameter and executes it (does not work for castling, en pessant, pawn promotion)
    '''

    def makeMove(self, move):
        self.board[move.startRow][move.startCol] = "--"
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.moveLog.append(move)
        self.whiteToMove = not self.whiteToMove  # swap players

        # update kings location if moved
        if move.pieceMoved == 'wK':
            self.wKingLoc == (move.endRow, move.endCol)
        elif move.pieceMoved == 'bK':
            self.bKingLoc == (move.endRow, move.endCol)

        #pawn promotion
        if move.isPawnPromotion:
            self.board[move.endRow][move.endCol] = move.pieceMoved[0] + 'Q' #takes color of promoted pawn and makes it a queen

        #enpessant move
        if move.isEnpessantMove:
            self.board[move.startRow][move.endCol] = '--' #capture the pawn

        #update enPessantPossible variable
        if move.pieceMoved[1] == 'p' and abs(move.startRow - move.endRow) == 2: #only on 2 square pawn advance
            self.enpessantPossible = ((move.startRow + move.endRow)//2, move.startCol)
        else:
            self.enpessantPossible = ()

        #castle move
        if move.isCastleMove:
            if move.endCol - move.startCol == 2: #kingside castle move
                self.board[move.endRow][move.endCol-1] = self.board[move.endRow][move.endCol+1] #moves the rook
                self.board[move.endRow][move.endCol+1] = '--' #erase old rook

            else: #queenside castle
                self.board[move.endRow][move.endCol+1] = self.board[move.endRow][move.endCol-2] #moves the rook
                self.board[move.endRow][move.endCol-2] = '--' #moves the rook

        #update castling rights - whenever it is a rook or a king move
        self.updateCastleRights(move)
        self.castleRightsLog.append(CastleRights(self.currentCastlingRight.wks, self.currentCastlingRight.bks,
                                             self.currentCastlingRight.wqs, self.currentCastlingRight.bqs))

    '''
    Undo the last move made
    '''
    def undoMove(self):
        if len(self.moveLog) != 0:  # make sure that there is a move to undo
            move = self.moveLog.pop()
            self.board[move.startRow][move.startCol] = move.pieceMoved  # moves piece back
            self.board[move.endRow][move.endCol] = move.pieceCaptured  # moves captured piece back
            self.whiteToMove = not self.whiteToMove  # swaps turn back

        # update kings location if moved
        if move.pieceMoved == 'wK':
            self.wKingLoc == (move.startRow, move.startCol)
        elif move.pieceMoved == 'bK':
            self.bKingLoc == (move.startRow, move.startCol)

        #undo enpessant move
        if move.isEnpessantMove:
            self.board[move.endRow][move.endCol] = '--' #leave landing square blank
            self.board[move.startRow][move.endCol] = move.pieceCaptured
            self.enpessantPossible = (move.endRow, move.endCol)
        #undo 2 square pawn advance
        if move.pieceMoved[1] == 'p' and abs(move.startRow - move.endRow) == 2:
            self.enpessantPossible = ()
        #undeo castling rights
        self.castleRightsLog.pop() #get rid of the new castle rights from the move we are undoing
        newRights = self.castleRightsLog[-1]
        self.currentCastlingRight = CastleRights(newRights.wks, newRights.bks, newRights.wqs, newRights.bqs) #set the current castling rights to the last one in the list
        #undo castle move
        if move.isCastleMove:
            if move.endCol - move.startCol == 2: #kingside
                self.board[move.endRow][move.endCol+1] = self.board[move.endRow][move.endCol-1]
                self.board[move.endRow][move.endCol-1] = '--'
            else: #queenside
                self.board[move.endRow][move.endCol-2] = self.board[move.endRow][move.endCol+1]
                self.board[move.endRow][move.endCol+1] = '--'

    '''
    Update the castle rights given the move
    '''
    def updateCastleRights(self, move):
        if move.pieceMoved == 'wK':
            self.currentCastlingRight.wks = False
            self.currentCastlingRight.wqs = False
        elif move.pieceMoved == 'bK':
            self.currentCastlingRight.bks = False
            self.currentCastlingRight.bqs = False
        elif move.pieceMoved == 'wR':
            if move.startRow == 7:
                if move.startCol == 0: #left rook
                    self.currentCastlingRight.wqs = False
                elif move.startCol == 7: #right rook
                    self.currentCastlingRight.wks = False
        elif move.pieceMoved == 'bR':
            if move.startRow == 0:
                if move.startCol == 0: #left rook
                    self.currentCastlingRight.bqs = False
                elif move.startCol == 7: #right rook
                    self.currentCastlingRight.bks = False

    '''
    All moves considering checks
    '''
    def getValidMoves(self):
        tempEnpessantPossible = self.enpessantPossible
        tempCastleRights = CastleRights(self.currentCastlingRight.wks, self.currentCastlingRight.bks,
                                        self.currentCastlingRight.wqs, self.currentCastlingRight.bqs) #copy the current castling rights
        # 1. generate all possible moves
        moves = self.getAllPossibleMoves()
        if self.whiteToMove:
            self.getCastleMoves(self.wKingLoc[0], self.wKingLoc[1], moves)
        else:
            self.getCastleMoves(self.bKingLoc[0], self.bKingLoc[1], moves)
        # 2. for each move, make the move
        for i in range(len(moves) - 1, -1, -1):  # when removing from a list always go backwards thru that list
            self.makeMove(moves[i])  # this switches the turns! need to switch back
            # 3. generate all opponent's moves
            # 4 for each of your opponents moves, see if they attack your king
            self.whiteToMove = not self.whiteToMove
            if self.inCheck():
                # 5 if they do, not a valid move
                moves.remove(moves[i])
            self.whiteToMove = not self.whiteToMove
            self.undoMove()

        if(len(moves)) == 0: #checkmate or stalemate
            if self.inCheck():
                self.checkmate = True
            else:
                self.stalemate = True
        else:
            self.checkmate = False
            self.stalemate = False

        self.enpessantPossible = tempEnpessantPossible
        self.currentCastlingRight = tempCastleRights

        return moves

    '''
    Determine if the current player is in check
    '''

    def inCheck(self):
        if self.whiteToMove:
            return self.squareUnderAttack(self.wKingLoc[0], self.wKingLoc[1])
        else:
            return self.squareUnderAttack(self.bKingLoc[0], self.bKingLoc[1])

    '''
    Determine if the enemy can attack the square r, c
    '''

    def squareUnderAttack(self, r, c):
        self.whiteToMove = not self.whiteToMove  # switch to opp's POV
        oppMoves = self.getAllPossibleMoves()
        self.whiteToMove = not self.whiteToMove  # switch turns back

        for move in oppMoves:
            if move.endRow == r and move.endCol == c:  # square is under attack
                return True
        return False

    '''
    All moves without considering checks
    '''

    def getAllPossibleMoves(self):
        moves = []  # Move((6,4), (4,4), self.board)
        for r in range(len(self.board)):
            for c in range(len(self.board[r])):
                color = self.board[r][c][0]  # the first character is always 'w' or 'b', aka whose piece it is
                if (color == 'w' and self.whiteToMove) or (color == 'b' and not self.whiteToMove):
                    piece = self.board[r][c][1]  # the second character is always the name of the piece
                    self.moveFunctions[piece](r, c, moves)  # calls appropriate move function based on piece type

        return moves

    '''
    Get all the pawn moves for the pawn located at row, col and add these moves to the list
    '''

    def getPawnMoves(self, r, c, moves):
        if self.whiteToMove:  # white pawn moves
            if self.board[r - 1][c] == '--':  # 1 square pawn advance
                moves.append(Move((r, c), (r - 1, c), self.board))
                if r == 6 and self.board[r - 2][c] == '--':  # 2 square pawn advance
                    moves.append(Move((r, c), (r - 2, c), self.board))
            if c - 1 >= 0:  # capture to left
                if self.board[r - 1][c - 1][0] == 'b':  # enemy piece to capture
                    moves.append(Move((r, c), (r - 1, c - 1), self.board))
                elif (r-1, c-1) == self.enpessantPossible:
                    moves.append(Move((r, c), (r - 1, c - 1), self.board, isEnpessantMove=True))

            if c + 1 <= 7:  # capture to right
                if self.board[r - 1][c + 1][0] == 'b':  # enemy piece to capture
                    moves.append(Move((r, c), (r - 1, c + 1), self.board))
                elif (r-1, c+1) == self.enpessantPossible:
                    moves.append(Move((r, c), (r - 1, c + 1), self.board, isEnpessantMove=True))
        else:  # black pawn moves
            if self.board[r + 1][c] == '--':  # 1 square pawn advance
                moves.append(Move((r, c), (r + 1, c), self.board))
                if r == 1 and self.board[r + 2][c] == '--':  # 2 square pawn advance
                    moves.append(Move((r, c), (r + 2, c), self.board))
            if c - 1 >= 0:  # capture to black's right
                if self.board[r + 1][c - 1][0] == 'w':  # enemy piece to capture
                    moves.append(Move((r, c), (r + 1, c - 1), self.board))
                elif (r+1, c-1) == self.enpessantPossible:
                    moves.append(Move((r, c), (r + 1, c - 1), self.board, isEnpessantMove=True))

            if c + 1 <= 7:  # capture to black's left
                if self.board[r + 1][c + 1][0] == 'w':  # enemy piece to capture
                    moves.append(Move((r, c), (r + 1, c + 1), self.board))
                elif (r+1, c+1) == self.enpessantPossible:
                    moves.append(Move((r, c), (r + 1, c + 1), self.board, isEnpessantMove=True))

    '''
    Get all the rook moves for the rook located at row, col and add these moves to the list
    '''

    def getRookMoves(self, r, c, moves):
        for rowAdder in range(-1, 2):
            for colAdder in range(-1, 2):
                if rowAdder.__abs__() == colAdder.__abs__():
                    continue
                ra = rowAdder
                ca = colAdder
                toContinue = True
                while toContinue and r + ra >= 0 and r + ra <= 7 and c + ca >= 0 and c + ca <= 7:
                    if self.board[r + ra][c + ca] == '--':
                        moves.append(Move((r, c), (r + ra, c + ca), self.board))
                        ra += rowAdder
                        ca += colAdder
                    elif self.board[r + ra][c + ca][0] == self.enemyPiece[self.whiteToMove]:
                        moves.append(Move((r, c), (r + ra, c + ca), self.board))
                        ra += rowAdder
                        ca += colAdder
                        toContinue = False
                    else:
                        toContinue = False

    '''
    Get all the knight moves for the knight located at row, col and add these moves to the list
    '''

    def getKnightMoves(self, r, c, moves):
        for rowAdder in range(-2, 3):
            if rowAdder == 0:
                continue
            else:
                colAdder = 3 - rowAdder.__abs__()
                halfComplete = 0
                while halfComplete < 2:
                    # print("RowAdder: " + str(rowAdder) + " ColAdder: " + str(colAdder))
                    # print("Row: " + str(r + rowAdder) + " Col: " + str(c + colAdder))
                    if r + rowAdder >= 0 and r + rowAdder <= 7 and c + colAdder >= 0 and c + colAdder <= 7:
                        if self.board[r + rowAdder][c + colAdder] == '--' or self.board[r + rowAdder][c + colAdder][
                            0] == self.enemyPiece[self.whiteToMove]:
                            moves.append(Move((r, c), (r + rowAdder, c + colAdder), self.board))
                    colAdder *= -1
                    halfComplete += 1

    '''
    Get all the bishop moves for the bishop located at row, col and add these moves to the list
    '''

    def getBishopMoves(self, r, c, moves):
        for rowAdder in range(-1, 2):
            for colAdder in range(-1, 2):
                if rowAdder.__abs__() != colAdder.__abs__() or (rowAdder == 0 and colAdder == 0):
                    continue
                ra = rowAdder
                ca = colAdder
                toContinue = True
                while toContinue and r + ra >= 0 and r + ra <= 7 and c + ca >= 0 and c + ca <= 7:
                    if self.board[r + ra][c + ca] == '--':
                        moves.append(Move((r, c), (r + ra, c + ca), self.board))
                        ra += rowAdder
                        ca += colAdder
                    elif self.board[r + ra][c + ca][0] == self.enemyPiece[self.whiteToMove]:
                        moves.append(Move((r, c), (r + ra, c + ca), self.board))
                        ra += rowAdder
                        ca += colAdder
                        toContinue = False
                    else:
                        toContinue = False

    '''
    Get all the Queen moves for the queen located at row, col and add these moves to the list
    '''

    def getQueenMoves(self, r, c, moves):
        self.getBishopMoves(r, c, moves)
        self.getRookMoves(r, c, moves)

    '''
    Get all the king moves for the king located at row, col and add these moves to the list
    '''

    def getKingMoves(self, r, c, moves):
        for rowAdder in range(-1, 2):
            for colAdder in range(-1, 2):
                if rowAdder == 0 and colAdder == 0:
                    continue
                if r + rowAdder >= 0 and r + rowAdder <= 7 and c + colAdder >= 0 and c + colAdder <= 7 and \
                        (self.board[r + rowAdder][c + colAdder] == '--' or self.board[r + rowAdder][c + colAdder][0] ==
                         self.enemyPiece[self.whiteToMove]):
                    moves.append(Move((r, c), (r + rowAdder, c + colAdder), self.board))

    '''
    Generate all valid castle moves for the king at (r, c) and add them to the list of moves
    '''
    def getCastleMoves(self, r, c, moves):
        if self.squareUnderAttack(r, c):
            return #cant castle when in check
        if (self.whiteToMove and self.currentCastlingRight.wks) or (not self.whiteToMove and self.currentCastlingRight.bks):
            self.getKingsideCastleMoves(r, c, moves)
        if(self.whiteToMove and self.currentCastlingRight.wqs) or (not self.whiteToMove and self.currentCastlingRight.bqs):
            self.getQueensideCastleMoves(r, c, moves)

    def getKingsideCastleMoves(self, r, c, moves):
        if self.board[r][c+1] == '--' and self.board[r][c+2] == '--':
            if not self.squareUnderAttack(r, c+1) and not self.squareUnderAttack(r, c+2):
                moves.append(Move((r, c), (r, c+2), self.board, isCastleMove=True))

    def getQueensideCastleMoves(self, r, c, moves):
        if self.board[r][c-1] == '--' and self.board[r][c-2] == '--' and self.board[r][c-3] == '--':
            if not self.squareUnderAttack(r, c-1) and not self.squareUnderAttack(r, c-2):
                moves.append(Move((r, c), (r, c+2), self.board, isCastleMove=True))

class CastleRights():
    def __init__(self, wks, bks, wqs, bqs):
        self.wks = wks
        self.bks = bks
        self.wqs = wqs
        self.bqs = bqs
class Move():
    # maps keys to values
    # key : value
    ranksToRows = {"1": 7, "2": 6, "3": 5, "4": 4,
                   "5": 3, "6": 2, "7": 1, "8": 0}
    rowsToRanks = {v: k for k, v in ranksToRows.items()}

    filesToCols = {"a": 0, "b": 1, "c": 2, "d": 3,
                   "e": 4, "f": 5, "g": 6, "h": 7}
    colsToFiles = {v: k for k, v in filesToCols.items()}

    def __init__(self, startSq, endSq, board, isEnpessantMove=False, isCastleMove=False):
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]
        self.isPawnPromotion = (self.pieceMoved == 'wp' and self.endRow == 0) or (self.pieceMoved == 'bp' and self.endRow == 7)
        self.isEnpessantMove = isEnpessantMove
        if self.isEnpessantMove:
            self.pieceCaptured = 'wp' if self.pieceMoved == 'bp' else 'bp'
        #castle move
        self.isCastleMove = isCastleMove

        self.moveID = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol
        # print(self.moveID)

    '''
    Overriding the equals method
    '''

    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False

    def getChessNotation(self):
        return self.getRankFile(self.startRow, self.startCol) + self.getRankFile(self.endRow, self.endCol)

    def getRankFile(self, r, c):
        return self.colsToFiles[c] + self.rowsToRanks[r]
