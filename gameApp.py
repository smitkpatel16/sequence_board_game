import logging
import threading
import time
import uuid
import json
import random
import tornado.web
import tornado.websocket
import numpy as np
from itertools import cycle
grid = [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]
BOARD = [["Joker", "TS", "QS", "KS", "AS", "2D", "3D", "4D", "5D", "Joker"],
         ["9S", "TH", "9H", "8H", "7H", "6H", "5H", "4H", "3H", "6D"],
         ["8S", "QH", "7D", "8D", "9D", "TD", "QD", "KD", "2H", "7D"],
         ["7S", "KH", "6D", "2C", "AH", "KH", "QH", "AD", "2S", "8D"],
         ["6S", "AH", "5D", "3C", "4H", "3H", "TH", "AC", "3S", "9D"],
         ["5S", "2C", "4D", "4C", "5H", "2H", "9H", "KC", "4S", "TD"],
         ["4S", "3C", "3D", "5C", "6H", "7H", "8H", "QC", "5S", "QD"],
         ["3S", "4C", "2D", "6C", "7C", "8C", "9C", "TC", "6S", "KD"],
         ["2S", "5C", "AS", "KS", "QS", "TS", "9S", "8S", "7S", "AD"],
         ["Joker", "6C", "7C", "8C", "9C", "TC", "QC", "KC", "AC", "Joker"]]
logger = logging.getLogger(__name__)
TEAMNAMES = ['#0000ff', '#00ff00', '#ff0000']
DECKOFCARDS = ['TC', 'TD', 'TH', 'TS', '2C', '2D', '2H', '2S', '3C',
               '3D', '3H', '3S', '4C', '4D', '4H', '4S', '5C', '5D', '5H',
               '5S', '6C', '6D', '6H', '6S', '7C', '7D', '7H', '7S', '8C',
               '8D', '8H', '8S', '9C', '9D', '9H', '9S', 'AC', 'AD', 'AH',
               'AS', 'JC', 'JD', 'JH', 'JS', 'KC', 'KD', 'KH', 'KS', 'QC',
               'QD', 'QH', 'QS', 'TC', 'TD', 'TH', 'TS', '2C', '2D',
               '2H', '2S', '3C', '3D', '3H', '3S', '4C', '4D', '4H', '4S',
               '5C', '5D', '5H', '5S', '6C', '6D', '6H', '6S', '7C', '7D',
               '7H', '7S', '8C', '8D', '8H', '8S', '9C', '9D', '9H', '9S',
               'AC', 'AD', 'AH', 'AS', 'JC', 'JD', 'JH', 'JS', 'KC', 'KD',
               'KH', 'KS', 'QC', 'QD', 'QH', 'QS']


def getCardsAndTeams(count):
    cards, teams = 0, 0
    if(count == 2):
        cards = 7
        teams = 2
    elif(count == 3):
        cards = 6
        teams = 3
    elif(count == 4):
        cards = 6
        teams = 2
    elif(count == 6):
        cards = 5
        teams = 3
    elif(count == 8):
        cards = 4
        teams = 2
    elif(count == 9):
        cards = 4
        teams = 3
    elif(count == 10):
        cards = 3
        teams = 2
    elif(count == 12):
        cards = 3
        teams = 3
    return cards, teams


# ===============================================================================
# MainHandler- Default request handler
# ===============================================================================
class MainHandler(tornado.web.RequestHandler):
    """Generic request handler that moves all http requests to https.
    """

    def prepare(self):
        pass
        # if self.request.protocol == 'http':
        #     self.redirect('https://' + self.request.host, permanent=True)

# ===============================================================================
# HomePage- Default homepage for hello
# ===============================================================================


class HomePage(MainHandler):
    def get(self):
        self.render("sources/index.html")


# ===============================================================================
# ChatRoomSocket- Stream Web cam and connect
# ===============================================================================
class GameSocket(tornado.websocket.WebSocketHandler):
    _ROOMCONNECTIONS = {}

    def open(self):
        self._name = None
        self._id = None
        self._master = False
        self._cards = []
        self._team = None
        self._turn = False

    def on_message(self, message):
        data = json.loads(message)
        if data.get('joinRoom'):
            # if the room is existing and the game is not started yet
            if data.get('joinRoom') in self._ROOMCONNECTIONS:
                gameRoom = self._ROOMCONNECTIONS[data.get('joinRoom')]
                if len(gameRoom['members']) < 12 and not gameRoom['game'] and self not in gameRoom['members']:
                    gameRoom['members'].append(self)
            # if the room is not existing
            else:
                self._ROOMCONNECTIONS[data.get('joinRoom')] = {}
                gameRoom = self._ROOMCONNECTIONS[data.get('joinRoom')]
                gameRoom['members'] = [self]
                gameRoom['occupied'] = {}
                gameRoom['boardCards'] = []
                gameRoom['game'] = False
            if not gameRoom['game']:
                gameRoom['deck'] = DECKOFCARDS[:]
                random.shuffle(gameRoom['deck'])
                if not any([member._master for member in gameRoom['members']]):
                    gameRoom['members'][0]._master = True
                if not self._name:
                    self._name = data.get('personName')
                if not self._id:
                    self._id = uuid.uuid4().hex[:8]
                logger.info("{} Joined the {} gameroom".format(self._name,
                                                               data.get('joinRoom')))
                count = len(
                    self._ROOMCONNECTIONS[data.get('joinRoom')]['members'])
                people = [
                    c._name+'_'+c._id for c in self._ROOMCONNECTIONS[data.get('joinRoom')]['members']]
                # peers = [
                #     c._id for c in self._ROOMCONNECTIONS[data.get('joinChat')]]
                for connection in self._ROOMCONNECTIONS[data.get('joinRoom')]['members']:
                    connection.write_message({'count': count,
                                              'people': people,
                                              'lastPeer': self._id,
                                              'id': connection._id,
                                              'master': self._master,
                                              'messageType': 'init'})
        else:
            # this is imperative without this we do not know which room to control
            gameID = data.get('gameID')
            gameRoom = self._ROOMCONNECTIONS[gameID]
            if gameID:
                count = len(gameRoom['members'])
                cards, teams = getCardsAndTeams(count)
                if data.get("messageType") == "text":
                    logger.info("{} messaged the {} chatroom".format(self._name,
                                                                     gameID))
                    for connection in gameRoom['members']:
                        connection.write_message({'count': count,
                                                  'messagePersonName': self._name,
                                                  'messageType':
                                                  data.get("messageType"),
                                                  'message':
                                                  data.get('message'),
                                                  'image':
                                                  data.get('image')
                                                  })
                if data.get('messageType') == 'start':
                    if self._master and not gameRoom['game'] and cards:
                        gameRoom['game'] = True
                        self._turn = True
                        random.shuffle(gameRoom['deck'])
                        for i, connection in enumerate(gameRoom['members'], start=1):
                            connection._cards = []
                            for c in range(cards):
                                connection._cards.append(
                                    gameRoom['deck'].pop(0))
                            connection._team = TEAMNAMES[i % teams]
                            connection.write_message({'messageType': 'start',
                                                      'cards': connection._cards,
                                                      'teams': teams,
                                                      'teamName': connection._team})
                            connection.write_message({'messageType': 'turn',
                                                      'memberid': self._id,
                                                      'teamName': self._team+'90'})

                if data.get('messageType') == "occupy" and self._turn:
                    self._occupyCard(data, gameRoom)
                    self._nextMemberTurn(gameID)
                if data.get('messageType') == "free" and self._turn:
                    self._freeUpCard(data, gameRoom)
                    self._nextMemberTurn(gameID)

# |-----------------------------------------------------------------------------|
# _occupyCard :-
# |-----------------------------------------------------------------------------|
    def _occupyCard(self, data, gameRoom):
        card = data.get("card")
        if card in self._cards:
            self._cards.remove(card)
            gameRoom['deck'].append(card)
        elif "JC" in self._cards:
            self._cards.remove("JC")
            gameRoom['deck'].append("JC")
        elif "JD" in self._cards:
            self._cards.remove("JD")
            gameRoom['deck'].append("JD")
        gameRoom['boardCards'].append(card)
        cardID = data.get("x")+'_'+data.get("y")+"_"+card
        newCard = gameRoom['deck'].pop(0)
        # dead card check
        while gameRoom['boardCards'].count(newCard) == 2:
            newCard = gameRoom['deck'].pop(0)
        self._cards.append(newCard)
        if self._team in gameRoom['occupied']:
            gameRoom['occupied'][self._team].append(
                (int(data.get("x")), int(data.get("y"))))
        else:
            gameRoom['occupied'][self._team] = [
                (int(data.get("x")), int(data.get("y")))]
        for connection in gameRoom['members']:
            connection.write_message({'messageType': 'occupy',
                                      'cardID': cardID,
                                      'teamName': self._team})
        self._monitorWins(gameRoom)
# |---------------------------End of _occupyCard--------------------------------|

#  |-----------------------------------------------------------------------------|
# _freeUpCard :-
# |-----------------------------------------------------------------------------|
    def _freeUpCard(self, data, gameRoom):
        card = data.get("card")
        if "JH" in self._cards:
            self._cards.remove("JH")
            gameRoom['deck'].append("JH")
        elif "JS" in self._cards:
            self._cards.remove("JS")
            gameRoom['deck'].append("JS")
        cardID = data.get("x")+'_'+data.get("y")+"_"+card
        frethis = (int(data.get("x")), int(data.get("y")))
        for key, values in gameRoom['occupied'].items():
            if frethis in values:
                gameRoom['occupied'][key].remove(frethis)
        gameRoom['boardCards'].remove(card)
        newCard = gameRoom['deck'].pop(0)
        # dead card check
        while gameRoom['boardCards'].count(newCard) == 2:
            newCard = gameRoom['deck'].pop(0)
        self._cards.append(newCard)
        for connection in gameRoom['members']:
            connection.write_message({'messageType': 'free',
                                      'cardID': cardID,
                                      'teamName': self._team})
# |--------------------------End of _freeUpCard---------------------------------|

# |-----------------------------------------------------------------------------|
# _monitorWins :-
# |-----------------------------------------------------------------------------|
    def _monitorWins(self, gameRoom):
        for key, values in gameRoom['occupied'].items():
            sortedVal = sorted(values, key=lambda k: [k[1], k[0]])
            tempGrid = np.array(grid[:])
            for val in sortedVal:
                tempGrid[val[0]][val[1]] = TEAMNAMES.index(key)+1
                tempGrid[0][0] = TEAMNAMES.index(key)+1
                tempGrid[9][9] = TEAMNAMES.index(key)+1
                tempGrid[0][9] = TEAMNAMES.index(key)+1
                tempGrid[9][0] = TEAMNAMES.index(key)+1
            subStr = "".join(5*[str(TEAMNAMES.index(key)+1)])
            winStreak = []
            winner = None
            for i in range(10):
                # for j in range(6):
                d = i-5
                dia = "".join([str(v) for v in tempGrid.diagonal(d)])
                dialr = "".join([str(v)
                                 for v in np.fliplr(tempGrid).diagonal(d)])
                col = "".join([str(v) for v in tempGrid[i, :]])
                row = "".join([str(v) for v in tempGrid[:, i]])
                # print(dia, row, col)
                if subStr in dia:
                    x = dia.index(subStr)
                    print("Dia ", d, x, dia)
                    print(gameRoom['occupied'][key])
                    if d >= 0:
                        for j in range(x, x+5):
                            if (j, d+j) not in [(0, 0), (0, 9), (9, 0), (9, 9)]:
                                gameRoom['occupied'][key].remove((j, d+j))
                            winStreak.append((j, d+j))
                            # print(j, d+j)
                    else:
                        for j in range(x, x+5):
                            if (abs(d)+j, j) not in [(0, 0), (0, 9), (9, 0), (9, 9)]:
                                gameRoom['occupied'][key].remove((abs(d)+j, j))
                            winStreak.append((abs(d)+j, j))
                            # print(abs(d)+j, j)
                    winner = key
                if subStr in dialr:
                    x = dialr.index(subStr)
                    print("DiaLR ", d, x, dialr)
                    print(gameRoom['occupied'][key])
                    if d >= 0:
                        for j in range(x-5, x):
                            if (9-j, d+j) not in [(0, 0), (0, 9), (9, 0), (9, 9)]:
                                gameRoom['occupied'][key].remove(
                                    (9-abs(d)+j, d+j))
                            winStreak.append((9-j, d+j))
                            # print(9-j, d+j)
                    else:
                        for j in range(x, x+5):
                            if (9-abs(d)+j, j) not in [(0, 0), (0, 9), (9, 0), (9, 9)]:
                                gameRoom['occupied'][key].remove(
                                    (9-abs(d)+j, j))
                            winStreak.append((9-abs(d)+j, j))
                            # print(9-abs(d)+j, j)
                    winner = key
                if subStr in row:
                    x = row.index(subStr)
                    print("Row ", i, x, row)
                    print(gameRoom['occupied'][key])
                    for j in range(x, x+5):
                        if (j, i) not in [(0, 0), (0, 9), (9, 0), (9, 9)]:
                            gameRoom['occupied'][key].remove((j, i))
                        winStreak.append((j, i))
                    winner = key
                if subStr in col:
                    x = col.index(subStr)
                    print("Col ", i, x, col)
                    print(gameRoom['occupied'][key])
                    for j in range(x, x+5):
                        if (i, j) not in [(0, 0), (0, 9), (9, 0), (9, 9)]:
                            gameRoom['occupied'][key].remove((i, j))
                        winStreak.append((i, j))
                    winner = key
        if winStreak:
            winStreak = [str(win[0])+"_"+str(win[1])+"_"+BOARD[win[1]][win[0]]
                         for win in winStreak]
            for connection in gameRoom['members']:
                connection.write_message({'messageType': 'win',
                                          'cardIDs': winStreak,
                                          'teamName': self._team})

# |--------------------------End of _monitorWins--------------------------------|


# |-----------------------------------------------------------------------------|
# _nextMemberTurn :-
# |-----------------------------------------------------------------------------|

    def _nextMemberTurn(self, gameID):
        # current member gets his/her new card
        self.write_message({"messageType": 'newCard',
                            "cards": self._cards})
        # find who is the next on list
        pool = cycle(self._ROOMCONNECTIONS[gameID]['members'])
        for member in pool:
            if member._turn:
                member._turn = False
                break
        member = next(pool)
        member._turn = True
        turnID = member._id
        teamName = member._team+'90'
        logger.info("{} cards in the deck".format(
            len(self._ROOMCONNECTIONS[gameID]['deck'])))
        for member in self._ROOMCONNECTIONS[gameID]['members']:
            member.write_message({'messageType': 'turn',
                                  'memberid': turnID,
                                  'teamName': teamName})
# |--------------------------End of _nextMemberTurn-----------------------------|

# |-----------------------------------------------------------------------------|
# on_close :-
# |-----------------------------------------------------------------------------|
    def on_close(self):
        for chatID, connectionBlock in self._ROOMCONNECTIONS.items():
            if self in connectionBlock['members']:
                self._ROOMCONNECTIONS[chatID]['members'].remove(self)
                self._ROOMCONNECTIONS[chatID]['game'] = False
                self._ROOMCONNECTIONS[chatID]['deck'] = DECKOFCARDS[:]
                logger.info("{} left {}".format(
                    self._name, chatID))
                count = len(self._ROOMCONNECTIONS[chatID]['members'])
                people = [
                    c._name+'_'+c._id for c in self._ROOMCONNECTIONS[chatID]['members']]
                for connection in self._ROOMCONNECTIONS[chatID]['members']:
                    connection.write_message({'peerId': self._id,
                                              'messageType': 'remove',
                                              'people': people,
                                              'count': count})
# |--------------------------End of on_close-----------------------------------|


# ===============================================================================
# Play- Main page to connect game rooms
# ===============================================================================
class Play(MainHandler):
    def get(self):
        self.render("sources/gameRoom.html")
