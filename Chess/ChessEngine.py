"""
Stores all info about current state of chess game and determining the valid moves
at current state.
Also keeps move log
"""


class GameState():
    def __init__(self):
        #board is 8x8 2d list each element of the list has 2 characters
        #first character represents color (b or w)
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
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"],]

        self.moveFunctions = {'p': self.getPawnMoves, 'R': self.getRookMoves, 'N': self.getKnightMoves, 'B': self.getBishopMoves,
                              'Q': self.getQueenMoves, 'K': self.getKingMoves}
        self.enemyPiece = {True: 'b', False: 'w'}

        self.whiteToMove = True
        self.moveLog = []
    '''
    Takes move as a parameter and executes it (does not work for castling, en pessant, pawn promotion)
    '''
    def makeMove(self, move):
        self.board[move.startRow][move.startCol] = "--"
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.moveLog.append(move)
        self.whiteToMove = not self.whiteToMove #swap players

    '''
    Undo the last move made
    '''
    def undoMove(self):
        if len(self.moveLog) != 0: #make sure that there is a move to undo
            move = self.moveLog.pop()
            self.board[move.startRow][move.startCol] = move.pieceMoved #moves piece back
            self.board[move.endRow][move.endCol] = move.pieceCaptured #moves captured piece back
            self.whiteToMove = not self.whiteToMove #swaps turn back

    '''
    All moves considering checks
    '''
    def getValidMoves(self):
        return self.getAllPossibleMoves() #for now we wont worry about checks

    '''
    All moves without considering checks
    '''
    def getAllPossibleMoves(self):
        moves = [] #Move((6,4), (4,4), self.board)
        for r in range(len(self.board)):
            for c in range(len(self.board[r])):
                color = self.board[r][c][0] #the first character is always 'w' or 'b', aka whose piece it is
                if (color == 'w' and self.whiteToMove) or (color == 'b' and not self.whiteToMove):
                    piece = self.board[r][c][1]  #the second character is always the name of the piece
                    self.moveFunctions[piece](r, c, moves) #calls appropriate move function based on piece type

        return moves


    '''
    Get all the pawn moves for the pawn located at row, col and add these moves to the list
    '''
    def getPawnMoves(self, r, c, moves):
        if self.whiteToMove: #white pawn moves
            if self.board[r-1][c] == '--': # 1 square pawn advance
                moves.append(Move((r, c), (r-1, c), self.board))
                if r == 6 and self.board[r-2][c] == '--': # 2 square pawn advance
                    moves.append(Move((r, c), (r-2, c), self.board))
            if c-1 >= 0: #capture to left
                if self.board[r-1][c-1][0] == 'b': #enemy piece to capture
                    moves.append(Move((r, c), (r-1, c-1), self.board))
            if c+1 <= 7: #capture to right
                if self.board[r-1][c+1][0] == 'b': #enemy piece to capture
                    moves.append(Move((r, c), (r-1, c+1), self.board))
        else: #black pawn moves
            if self.board[r+1][c] == '--': # 1 square pawn advance
                moves.append(Move((r, c), (r+1, c), self.board))
                if r == 1 and self.board[r+2][c] == '--': # 2 square pawn advance
                    moves.append(Move((r, c), (r+2, c), self.board))
            if c-1 >= 0: #capture to black's right
                if self.board[r+1][c-1][0] == 'w': #enemy piece to capture
                    moves.append(Move((r, c), (r+1, c-1), self.board))
            if c+1 <= 7: #capture to black's left
                if self.board[r+1][c+1][0] == 'w': #enemy piece to capture
                    moves.append(Move((r, c), (r+1, c+1), self.board))

    '''
    Get all the rook moves for the rook located at row, col and add these moves to the list
    '''
    def getRookMoves(self, r, c, moves):
        count = 1 #checking upwards
        while r-count >= 0 and self.board[r-count][c] == '--':
            moves.append(Move((r, c), (r-count, c), self.board))
            count += 1
        if r-count >= 0 and self.board[r-count][c][0] == self.enemyPiece[self.whiteToMove]:
             moves.append(Move((r, c), (r-count, c), self.board))

        count = 1 #checking downwards
        while r+count <= 7 and self.board[r+count][c] == '--':
            moves.append(Move((r, c), (r+count, c), self.board))
            count += 1
        if r+count <= 7 and self.board[r+count][c][0] == self.enemyPiece[self.whiteToMove]:
            moves.append(Move((r, c), (r+count, c), self.board))

        count = 1 #checking left
        while c-count >= 0 and self.board[r][c-count] == '--': ##checking left
            moves.append(Move((r, c), (r, c-count), self.board))
            count += 1
        if c-count >= 0 and self.board[r][c-count][0] == self.enemyPiece[self.whiteToMove]:
            moves.append(Move((r, c), (r, c-count), self.board))

        count = 1 #checking right
        while c+count <= 7 and self.board[r][c+count] == '--':
            moves.append(Move((r, c), (r, c+count), self.board))
            count += 1
        if c+count <= 7 and self.board[r][c+count][0] == self.enemyPiece[self.whiteToMove]:
            moves.append(Move((r, c), (r, c+count), self.board))

    '''
    Get all the knight moves for the rook located at row, col and add these moves to the list
    '''
    def getKnightMoves(self, r, c, moves):
        print("\n\n\n\n" + str(self.whiteToMove))
        for rowAdder in range (-2,3):
            if rowAdder == 0:
                continue
            else:
                colAdder = 3 - rowAdder.__abs__()
                halfComplete = 0
                while halfComplete < 2:
                    #print("RowAdder: " + str(rowAdder) + " ColAdder: " + str(colAdder))
                    #print("Row: " + str(r + rowAdder) + " Col: " + str(c + colAdder))
                    if r + rowAdder >= 0 and r + rowAdder <= 7 and c + colAdder >= 0 and c + colAdder <= 7:
                        if self.board[r+rowAdder][c+colAdder] == '--' or self.board[r+rowAdder][c+colAdder][0] == self.enemyPiece[self.whiteToMove]:
                            moves.append(Move((r, c), (r+rowAdder, c+colAdder), self.board))
                    colAdder *= -1
                    halfComplete +=1

        # #rowAdder = -2
        # colAdder= -2
        # increaseRows = False
        # while(colAdder < 3 and rowAdder < 3):
        #     if(rowAdder.__abs__() + colAdder.__abs__() == 3):
        #         if(r+rowAdder >= 0 and r+rowAdder <= 7 and c+colAdder >= 0 and c+colAdder <= 7):
        #             if(self.board[r+rowAdder][c+colAdder] == '--' or self.board[r+rowAdder][c+colAdder] == self.enemyPiece[self.whiteToMove]):
        #                 moves.append(Move((r, c), (r+rowAdder, c+colAdder), self.board))
        #                 if(increaseRows == False and colAdder == 2):
        #                     increaseRows = True
        #                     colAdder =
        #                 else:
        #                     colAdder += 1

    '''
    Get all the bishop moves for the rook located at row, col and add these moves to the list
    '''
    def getBishopMoves(self, r, c, moves):
        count = 1 #checking up&left
        while r-count >= 0 and c-count >= 0 and self.board[r-count][c-count] == '--':
            moves.append(Move((r, c), (r-count, c-count), self.board))
            count += 1
        if r-count >= 0 and c-count >= 0 and self.board[r-count][c-count][0] == self.enemyPiece[self.whiteToMove]:
             moves.append(Move((r, c), (r-count, c-count), self.board))

        count = 1 #checking down&left
        while r+count <= 7 and c-count >= 0 and self.board[r+count][c-count] == '--':
            moves.append(Move((r, c), (r+count, c-count), self.board))
            count += 1
        if r+count <= 7 and c-count >= 0 and self.board[r+count][c-count][0] == self.enemyPiece[self.whiteToMove]:
            moves.append(Move((r, c), (r+count, c-count), self.board))

        count = 1 #checking up&right
        while r-count >= 0 and c+count <= 7 and self.board[r-count][c+count] == '--': ##checking left
            moves.append(Move((r, c), (r-count, c+count), self.board))
            count += 1
        if r-count >= 0 and c+count <= 7 and self.board[r-count][c+count][0] == self.enemyPiece[self.whiteToMove]:
            moves.append(Move((r, c), (r-count, c+count), self.board))

        count = 1 #checking down&right
        while r+count <= 7 and c+count <= 7 and self.board[r+count][c+count] == '--':
            moves.append(Move((r, c), (r+count, c+count), self.board))
            count += 1
        if r+count <= 7 and c+count <= 7 and self.board[r+count][c+count][0] == self.enemyPiece[self.whiteToMove]:
            moves.append(Move((r, c), (r+count, c+count), self.board))

    '''
    Get all the Queen moves for the rook located at row, col and add these moves to the list
    '''
    def getQueenMoves(self, r, c, moves):
        count = 1 #checking upwards
        while r-count >= 0 and self.board[r-count][c] == '--':
            moves.append(Move((r, c), (r-count, c), self.board))
            count += 1
        if r-count >= 0 and self.board[r-count][c][0] == self.enemyPiece[self.whiteToMove]:
             moves.append(Move((r, c), (r-count, c), self.board))

        count = 1 #checking downwards
        while r+count <= 7 and self.board[r+count][c] == '--':
            moves.append(Move((r, c), (r+count, c), self.board))
            count += 1
        if r+count <= 7 and self.board[r+count][c][0] == self.enemyPiece[self.whiteToMove]:
            moves.append(Move((r, c), (r+count, c), self.board))

        count = 1 #checking left
        while c-count >= 0 and self.board[r][c-count] == '--': ##checking left
            moves.append(Move((r, c), (r, c-count), self.board))
            count += 1
        if c-count >= 0 and self.board[r][c-count][0] == self.enemyPiece[self.whiteToMove]:
            moves.append(Move((r, c), (r, c-count), self.board))

        count = 1 #checking right
        while c+count <= 7 and self.board[r][c+count] == '--':
            moves.append(Move((r, c), (r, c+count), self.board))
            count += 1
        if c+count <= 7 and self.board[r][c+count][0] == self.enemyPiece[self.whiteToMove]:
            moves.append(Move((r, c), (r, c+count), self.board))

        count = 1 #checking up&left
        while r-count >= 0 and c-count >= 0 and self.board[r-count][c-count] == '--':
            moves.append(Move((r, c), (r-count, c-count), self.board))
            count += 1
        if r-count >= 0 and c-count >= 0 and self.board[r-count][c-count][0] == self.enemyPiece[self.whiteToMove]:
             moves.append(Move((r, c), (r-count, c-count), self.board))

        count = 1 #checking down&left
        while r+count <= 7 and c-count >= 0 and self.board[r+count][c-count] == '--':
            moves.append(Move((r, c), (r+count, c-count), self.board))
            count += 1
        if r+count <= 7 and c-count >= 0 and self.board[r+count][c-count][0] == self.enemyPiece[self.whiteToMove]:
            moves.append(Move((r, c), (r+count, c-count), self.board))

        count = 1 #checking up&right
        while r-count >= 0 and c+count <= 7 and self.board[r-count][c+count] == '--': ##checking left
            moves.append(Move((r, c), (r-count, c+count), self.board))
            count += 1
        if r-count >= 0 and c+count <= 7 and self.board[r-count][c+count][0] == self.enemyPiece[self.whiteToMove]:
            moves.append(Move((r, c), (r-count, c+count), self.board))

        count = 1 #checking down&right
        while r+count <= 7 and c+count <= 7 and self.board[r+count][c+count] == '--':
            moves.append(Move((r, c), (r+count, c+count), self.board))
            count += 1
        if r+count <= 7 and c+count <= 7 and self.board[r+count][c+count][0] == self.enemyPiece[self.whiteToMove]:
            moves.append(Move((r, c), (r+count, c+count), self.board))
    '''
    Get all the king moves for the rook located at row, col and add these moves to the list
    '''
    def getKingMoves(self, r, c, moves):
        if r-1 >= 0 and (self.board[r-1][c] == '--' or self.enemyPiece[self.whiteToMove]):
            moves.append(Move((r, c), (r-1, c), self.board))

        if r+1 <= 7 and (self.board[r+1][c] == '--' or self.enemyPiece[self.whiteToMove]):
            moves.append(Move((r, c), (r+1, c), self.board))

        if c-1 >= 0 and (self.board[c-1][c] == '--' or self.enemyPiece[self.whiteToMove]):
            moves.append(Move((r, c), (c-1, c), self.board))

        if c+1 <= 7 and (self.board[c+1][c] == '--' or self.enemyPiece[self.whiteToMove]):
            moves.append(Move((r, c), (c+1, c), self.board))



class Move():
    #maps keys to values
    #key : value
    ranksToRows = {"1": 7, "2": 6, "3": 5, "4": 4,
                   "5": 3, "6": 2, "7": 1, "8": 0}
    rowsToRanks = {v: k for k, v in ranksToRows.items()}

    filesToCols = {"a": 0, "b": 1, "c": 2, "d": 3,
                   "e": 4, "f": 5, "g": 6, "h": 7}
    colsToFiles = {v: k for k, v in filesToCols.items()}

    def __init__(self, startSq, endSq, board):
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]
        self.moveID = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol
        #print(self.moveID)

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

