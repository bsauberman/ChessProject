"""
Main driver files responsible for user input and displaying current GameState object
"""
from Chess import ChessEngine
import pygame as p

WIDTH = HEIGHT = 512
DIMENSION = 8 #dimensions of chess board are 8x8
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 15 #for animation
IMAGES = {}

'''
Initialize a global dictionary of images. Will be called exactly once
'''

def loadImages():
    pieces = ['wp', 'wR', 'wN', 'wB', 'wQ', 'wK', 'bp', 'bR', 'bN', 'bB', 'bQ', 'bK']
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load("Chess/images/" + piece + ".png"), (SQ_SIZE, SQ_SIZE))
        #NOTE: can access an image by saying 'IMAGES['wp']'

'''
The main driver for our code that handles user input and updating graphics
'''

def main():
    p.init()
    screen = p.display.set_mode((WIDTH,HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    gs = ChessEngine.GameState()
    validMoves = gs.getValidMoves()
    moveMade = False #flag variable for when a valid move is made and gamestate actually changes

    animate = False # flag variable for when we should animate a move
    loadImages() #only do once, before while loop
    running = True
    sqSelected = () #no square is selected, keep track of last click of user (tuple: row, col)
    playerClicks = [] #keep track of player clicks (two tuples: [(6,4), (4,4)])
    gameOver = False

    print(validMoves)


    while running:
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            #mouse handler
            elif e.type == p.MOUSEBUTTONDOWN:
                if not gameOver:
                    location = p.mouse.get_pos() #(x,y location of mouse)
                    col = location[0] // SQ_SIZE
                    row = location[1] // SQ_SIZE
                    if sqSelected == (row, col): #user clicked same square twice
                        sqSelected = ()
                        playerClicks = [] #clear player clicks
                    else:
                        sqSelected = (row, col)
                        playerClicks.append(sqSelected) #append for both 1st and 2nd clicks
                    if len(playerClicks) == 2: #after 2nd click
                        move = ChessEngine.Move(playerClicks[0], playerClicks[1], gs.board)
                        print(move.getChessNotation())
                        for i in range(len(validMoves)):
                            if move == validMoves[i]:
                                gs.makeMove(validMoves[i]) #instead of using "move", we make sure to use validMoves[i] bc those have the necessary flags
                                moveMade = True
                                animate = True
                                sqSelected = () #reset user clicks
                                playerClicks = []
                        if not moveMade:
                            playerClicks = [sqSelected]
                    #key handler
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z: #undo when 'z' is pressed
                    gs.undoMove()
                    moveMade = True
                    animate = False
                if e.key == p.K_r: #reset the board when r is pressed
                    gs = ChessEngine.GameState()
                    validMoves = gs.getValidMoves()
                    sqSelected = ()
                    playerClicks = []
                    moveMade = False
                    animate = False
        if moveMade:
            if animate:
                animateMove(gs.moveLog[-1], screen, gs.board, clock)
            validMoves = gs.getValidMoves()
            # print("\nUpdated Valid Moves:")
            # count = 0
            # for i in range(len(validMoves)):
            #     if(validMoves[i].pieceMoved[1] == 'B'):
            #         print(validMoves[i].moveID)
            #         count+=1
            moveMade = False
            animate = False

        drawGameState(screen, gs, validMoves, sqSelected)

        if gs.checkmate:
            gameOver = True
            if gs.whiteToMove:
                drawText(screen, 'Black wins by checkmate')
            else:
                drawText(screen, 'White wins by checkmate')
        elif gs.stalemate:
            gameOver = True
            drawText(screen, 'Stalemate')
        clock.tick(MAX_FPS)
        p.display.flip()

'''
Highlight square selected and moves for piece selected
'''
def highlightSquares(screen, gs, validMoves, sqSelected):
    if sqSelected != ():
        r, c = sqSelected
        if gs.board[r][c][0] != (gs.enemyPiece[gs.whiteToMove]): #check if sqSelected is a piece that can be moved
            s = p.Surface((SQ_SIZE, SQ_SIZE))
            s.set_alpha(100) #transparency value -> 0 transparent; 255 opaque
            s.fill(p.Color('blue'))
            screen.blit(s, (c*SQ_SIZE, r*SQ_SIZE))
            #highlight moves from that square
            s.fill(p.Color('yellow'))
            for move in validMoves:
                if move.startRow == r and move.startCol == c:
                    screen.blit(s, (SQ_SIZE*move.endCol, SQ_SIZE*move.endRow))





'''
Responsible for all the graphics within a current game state
'''
def drawGameState(screen, gs, validMoves, sqSelected):
    drawBoard(screen) #draw  es onto board
    highlightSquares(screen, gs, validMoves, sqSelected)
    drawPieces(screen, gs.board) #draw pieces on top of squares

'''
Draw the squares on the board top left square is always light
'''
def drawBoard(screen):
    global colors
    colors = [p.Color("white"), p.Color("gray")]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[((r+c) % 2)]
            p.draw.rect(screen, color, p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE,))


'''
Draw the pieces on the board using the current GameState.board
'''
def drawPieces(screen, board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != "--": #not empty square
                screen.blit(IMAGES[piece], p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))

'''
Animating a move
'''
def animateMove(move, screen, board, clock):
    global colors
    coords = [] #list of coords that the animation will move through
    dR = move.endRow - move.startRow
    dC = move.endCol - move.startCol
    framesPerSquare = 7 #frames to move one square
    frameCount = (abs(dR) + abs(dC)) * framesPerSquare
    for frame in range(frameCount + 1):
        r, c = (move.startRow + dR*frame/frameCount, move.startCol + dC*frame/frameCount)
        drawBoard(screen)
        drawPieces(screen, board)
        #erase the piece moved from its ending square
        color = colors[(move.endRow + move.endCol) % 2]
        endSquare = p.Rect(move.endCol*SQ_SIZE, move.endRow*SQ_SIZE, SQ_SIZE, SQ_SIZE) #draws a square of the same color over that square, thereby 'erasing' the piece
        p.draw.rect(screen, color, endSquare)
        #draw captured piece onto rectangle
        if move.pieceCaptured != '--':
            screen.blit(IMAGES[move.pieceCaptured], endSquare)
        #draw moving piece
        screen.blit(IMAGES[move.pieceMoved], p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))
        p.display.flip() #updates fulld isplay to screen
        clock.tick(60)

def drawText(screen, text):
    font = p.font.SysFont("Helvitca", 32, True, False)
    textObject = font.render(text, 0, p.Color('Gray'))
    textLocation = p.Rect(0, 0, WIDTH, HEIGHT).move(WIDTH/2 - textObject.get_width()/2, HEIGHT/2 - textObject.get_height()/2)
    screen.blit(textObject, textLocation)
    textObject = font.render(text, 0, p.Color('Black'))
    screen.blit(textObject, textLocation.move(2,2))


if __name__ == '__main__':
    main()
