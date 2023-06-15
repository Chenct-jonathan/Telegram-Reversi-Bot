#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, CommandHandler, CallbackQueryHandler
import json
with open("token.info", "r", encoding="utf-8") as jFILE:
    token = json.load(jFILE)["token"]
import random
import time
from collections import Counter

black = '⚫️'
white = '⚪️'


def enc(board):
    # board is a dictionary mapping (row, col) to grid
    # grid = [[board.get((row, col), '') for col in range(8)] for row in range(8)]
    number = 0
    base = 3
    for row in range(8):
        for col in range(8):
            number *= base
            # if grid[row][col] == black:
            if board.get((row, col)) == black:
                number += 2
            # elif grid[row][col] == white:
            elif board.get((row, col)) == white:
                number += 1
    #print(number)
    return str(number)

def dec(number):
    board = {}
    base = 3
    for row in range(7, -1, -1):
        for col in range(7, -1, -1):
            if number % 3 == 2:
                board[(row, col)] = black
            elif number % 3 == 1:
                board[(row, col)] = white
            number //= base
    #print(board)
    return board

def board_markup(board):
    # board will be encoded and embedded to callback_data
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(board.get((row, col), f'{row},{col}'), callback_data=f'{row}{col}{enc(board)}') for col in range(8)]
        for row in range(8)])

def isInBound(dropPos):
    x = dropPos[0]
    y = dropPos[1]
    if x >= 0 and x <= 7 and y >= 0 and y <= 7:
        return True
    else:
        return False

def isValidMove(board, dropPos, dropColor):
    if dropPos in board.keys():
        #print('duplicate')
        return False
    flipLIST = []
    for xdir, ydir in [ [0, 1], [1, 1], [1, 0], [1, -1], [0, -1], [-1, -1], [-1, 0], [-1, 1] ]:
        x = dropPos[0]
        y = dropPos[1]
        x += xdir
        y += ydir
        if isInBound((x, y))==True and (x, y) in board.keys():
            if board[(x, y)] != dropColor:
                pass
            else:
                continue
        else:
            continue
        x += xdir
        y += ydir
        if isInBound((x, y)) == False or (x, y) not in board.keys():
            continue
        else:
            while (x, y) in board.keys() and board[(x, y)] != dropColor:                
                x += xdir
                y += ydir
                if isInBound((x, y)) == False:
                    break
            if isInBound((x, y)) == False:
                continue
            if (x, y) in board.keys() and board[(x, y)] == dropColor:
                while True:
                    x -= xdir
                    y -= ydir
                    if x == dropPos[0] and y == dropPos[1]:
                        break
                    # 需要翻轉的棋子
                    flipLIST.append((x, y))
    if len(flipLIST) == 0:
        #print(flipLIST)
        return False
    #print(flipLIST)
    return flipLIST

def getValidMove(board, dropColor):
    validLIST = []
    for x in range(8):
        for y in range(8):
            #print(f'now checking ({x}, {y})')
            if isValidMove(board, (x, y), dropColor) != False:
                validLIST.append((x, y))
    return validLIST

def count_all(board):
    result = Counter(board.values())
    if result[black] > result[white]:
        return 'black wins'
    elif  result[black] < result[white]:
        return 'white wins'
    else:
        return 'tie'

def check_game(board):
    if getValidMove(board, black) == [] and getValidMove(board, white) == []:
        #print(count_all(board))
        return count_all(board)
    else:
        #print('game continue')
        return 'game continue'

async def dropBlack(update, context):
    data = update.callback_query.data
    row = int(data[0])
    col = int(data[1])
    clickPos = (row, col)
    board = dec(int(data[2:]))
    flipWhiteLIST= isValidMove(board, clickPos, black)
    if flipWhiteLIST != False:
        await context.bot.answer_callback_query(update.callback_query.id, f'black go ({row} , {col})')
        board[(row, col)] = black
        await context.bot.edit_message_text(f'/ Reversi/ Current Game Continue/ Black Go {clickPos}',
                                            reply_markup=board_markup(board),
                                            chat_id=update.callback_query.message.chat_id,
                                            message_id=update.callback_query.message.message_id)        
        
        time.sleep(1)
        for i in flipWhiteLIST:
            board[i] = black
        print(f'blackMove {clickPos}')
        print(f'flip {flipWhiteLIST}')
        gameStatus = check_game(board)
        if gameStatus == 'game continue':
            print('GameContinue')
            await context.bot.edit_message_text('/ Reversi/ Current Game Continue/ Opponent\'s Turn',
                                                reply_markup=board_markup(board),
                                                chat_id=update.callback_query.message.chat_id,
                                                message_id=update.callback_query.message.message_id)
        elif  gameStatus == 'black wins':
            print('Game Over, Black Wins')
            await context.bot.edit_message_text('/ Reversi/ Current Game End/ Black Wins',
                                                reply_markup=board_markup(board),
                                                chat_id=update.callback_query.message.chat_id,
                                                message_id=update.callback_query.message.message_id)
            return
        
        elif  gameStatus == 'white wins':
            print('Game Over, White Wins')
            await context.bot.edit_message_text('/ Reversi/ Current Game End/ White Wins',
                                                reply_markup=board_markup(board),
                                                chat_id=update.callback_query.message.chat_id,
                                                message_id=update.callback_query.message.message_id)
            return
        
        elif  gameStatus == 'tie':
            print('Game Over, Tie')
            await context.bot.edit_message_text('/ Reversi/ Current Game End/ Tie',
                                                reply_markup=board_markup(board),
                                                chat_id=update.callback_query.message.chat_id,
                                                message_id=update.callback_query.message.message_id)
            return
        
        else:
            pass
        await dropWhite(board, update, context)
        if getValidMove(board, black) == []:
            await dropWhite(board, update, context)
        else:
            pass
    else:
        print('invalid move')
        await context.bot.answer_callback_query(update.callback_query.id, f'({row} , {col}) is invalid')
        gameStatus = check_game(board)
        if  gameStatus == 'black wins':
            print('Game Over, Black Wins')
            await context.bot.edit_message_text('/ Reversi/ Current Game End/ Black Wins',
                                                reply_markup=board_markup(board),
                                                chat_id=update.callback_query.message.chat_id,
                                                message_id=update.callback_query.message.message_id)
            return
        
        elif  gameStatus == 'white wins':
            print('Game Over, White Wins')
            await context.bot.edit_message_text('/ Reversi/ Current Game End/ White Wins',
                                                reply_markup=board_markup(board),
                                                chat_id=update.callback_query.message.chat_id,
                                                message_id=update.callback_query.message.message_id)
            return
        
        elif  gameStatus == 'tie':
            print('Game Over, Tie')
            await context.bot.edit_message_text('/ Reversi/ Current Game End/ Tie',
                                                reply_markup=board_markup(board),
                                                chat_id=update.callback_query.message.chat_id,
                                                message_id=update.callback_query.message.message_id)
            return
        
        else:
            pass
        
async def dropWhite(board, update, context):
    gameStatus = check_game(board)
    if  gameStatus == 'black wins':
        print('Game Over, Black Wins')
        await context.bot.edit_message_text('/ Reversi/ Current Game End/ Black Wins',
                                            reply_markup=board_markup(board),
                                            chat_id=update.callback_query.message.chat_id,
                                            message_id=update.callback_query.message.message_id)
        return
    
    elif  gameStatus == 'white wins':
        print('Game Over, White Wins')
        await context.bot.edit_message_text('/ Reversi/ Current Game End/ White Wins',
                                            reply_markup=board_markup(board),
                                            chat_id=update.callback_query.message.chat_id,
                                            message_id=update.callback_query.message.message_id)
        return
    
    elif  gameStatus == 'tie':
        print('Game Over, Tie')
        await context.bot.edit_message_text('/ Reversi/ Current Game End/ Tie',
                                            reply_markup=board_markup(board),
                                            chat_id=update.callback_query.message.chat_id,
                                            message_id=update.callback_query.message.message_id)
        return
    
    else:
        pass    
    validLIST = getValidMove(board, white)
    if validLIST != []:
        index = random.randint(0, len(validLIST) - 1)
        whiteMove = validLIST[index]
        print(f'white move {whiteMove}')
        flipBlackLIST = isValidMove(board, whiteMove, white)
        print(flipBlackLIST)
        if flipBlackLIST != False:
            board[whiteMove] = white
            await context.bot.edit_message_text(f'/ Reversi/ Current Game Continue/ White Go {whiteMove}',
                                                reply_markup=board_markup(board),
                                                chat_id=update.callback_query.message.chat_id,
                                                message_id=update.callback_query.message.message_id)
            time.sleep(1)
            for i in flipBlackLIST:
                print(f'flip {i}')
                board[i] = white             
        #board[whiteMove] = white
        gameStatus = check_game(board)
        if gameStatus == 'game continue':
            print('GameContinue')
            await context.bot.edit_message_text('/ Reversi/ Current Game Continue/ Your Turn',
                                                reply_markup=board_markup(board),
                                                chat_id=update.callback_query.message.chat_id,
                                                message_id=update.callback_query.message.message_id)
        elif  gameStatus == 'black wins':
            print('Game Over, Black Wins')
            await context.bot.edit_message_text('/ Reversi/ Current Game End/ Black Wins',
                                                reply_markup=board_markup(board),
                                                chat_id=update.callback_query.message.chat_id,
                                                message_id=update.callback_query.message.message_id)
            return
        
        elif  gameStatus == 'white wins':
            print('Game Over, White Wins')
            await context.bot.edit_message_text('/ Reversi/ Current Game End/ White Wins',
                                                reply_markup=board_markup(board),
                                                chat_id=update.callback_query.message.chat_id,
                                                message_id=update.callback_query.message.message_id)
            return
        
        elif  gameStatus == 'tie':
            print('Game Over, Tie')
            await context.bot.edit_message_text('/ Reversi/ Current Game End/ Tie',
                                                reply_markup=board_markup(board),
                                                chat_id=update.callback_query.message.chat_id,
                                                message_id=update.callback_query.message.message_id)
            return
        
        else:
            pass
        #time.sleep(2)
        #if getValidMove(board, white) == [] and getValidMove(board, black) == []:
            #print('all out of moves, game over')
            #gameState = check_game(board)
            #await context.bot.answer_callback_query(update.callback_query.id, gameState)            
    else:
        print('white out of moves')
        gameStatus = check_game(board)
        await context.bot.answer_callback_query(update.callback_query.id, 'There are no valid moves for white.')
        if  gameStatus == 'black wins':
            print('Game Over, Black Wins')
            await context.bot.edit_message_text('/ Reversi/ Current Game End/ Black Wins',
                                                reply_markup=board_markup(board),
                                                chat_id=update.callback_query.message.chat_id,
                                                message_id=update.callback_query.message.message_id)
            return
        
        elif  gameStatus == 'white wins':
            print('Game Over, White Wins')
            await context.bot.edit_message_text('/ Reversi/ Current Game End/ White Wins',
                                                reply_markup=board_markup(board),
                                                chat_id=update.callback_query.message.chat_id,
                                                message_id=update.callback_query.message.message_id)
            return
        
        elif  gameStatus == 'tie':
            print('Game Over, Tie')
            await context.bot.edit_message_text('/ Reversi/ Current Game End/ Tie',
                                                reply_markup=board_markup(board),
                                                chat_id=update.callback_query.message.chat_id,
                                                message_id=update.callback_query.message.message_id)
            return
        
        else:
            print('GameContinue')
            await context.bot.edit_message_text('/ Reversi/ Current Game Continue/ Your Turn',
                                                reply_markup=board_markup(board),
                                                chat_id=update.callback_query.message.chat_id,
                                                message_id=update.callback_query.message.message_id)
            
async def start(update, context):
    board = {(3,3): '⚫️', (3,4): '⚪️', (4,3): '⚪️', (4,4): '⚫️'}
    # reply_markup = board_markup(board)
    await update.message.reply_text('/ Reversi/ New Game/ Your Turn', reply_markup=board_markup(board))
    
def main():
    """Start the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(token).build()

    # on different commands - answer in Telegram    
    application.add_handler(CommandHandler("game_start", start))

    application.add_handler(CallbackQueryHandler(dropBlack))

    # Run the bot until the user presses Ctrl-C
    application.run_polling()

#loop = asyncio.get_event_loop()

if __name__ == "__main__":
    main()
    
def main():
    """Start the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(token).build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("restart", start))    
    application.add_handler(CommandHandler("game_start", start))

    application.add_handler(CallbackQueryHandler(dropBlack))

    # Run the bot until the user presses Ctrl-C
    application.run_polling()


if __name__ == "__main__":
    main()