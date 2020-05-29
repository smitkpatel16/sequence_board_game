import logging
import threading
import time
import uuid
import json
import random
import tornado.web
import tornado.websocket
from itertools import cycle

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
            if data.get('joinRoom') in self._ROOMCONNECTIONS:
                gameRoom = self._ROOMCONNECTIONS[data.get('joinRoom')]
                if len(gameRoom['members']) < 12 and not gameRoom['game'] and self not in gameRoom['members']:
                    gameRoom['members'].append(self)
            else:
                self._ROOMCONNECTIONS[data.get('joinRoom')] = {}
                gameRoom = self._ROOMCONNECTIONS[data.get('joinRoom')]
                gameRoom['members'] = [self]
            gameRoom['deck'] = DECKOFCARDS[:]
            random.shuffle(gameRoom['deck'])
            gameRoom['game'] = False
            if not any([member._master for member in gameRoom['members']]):
                gameRoom['members'][0]._master = True
            if not self._name:
                self._name = data.get('personName')
            if not self._id:
                self._id = uuid.uuid4().hex[:8]
            logger.info("{} Joined the {} gameroom".format(self._name,
                                                           data.get('joinRoom')))
            count = len(self._ROOMCONNECTIONS[data.get('joinRoom')]['members'])
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
                        for i, connection in enumerate(gameRoom['members'], start=1):
                            for c in range(cards):
                                connection._cards.append(
                                    gameRoom['deck'].pop())
                            connection._team = TEAMNAMES[i % teams]
                            connection.write_message({'messageType': 'start',
                                                      'cards': connection._cards,
                                                      'teams': teams,
                                                      'teamName': connection._team})
                            connection.write_message({'messageType': 'turn',
                                                      'memberid': self._id,
                                                      'teamName': self._team+'90'})

                if data.get('messageType') == "occupy" and self._turn:
                    card = data.get("card")
                    if card in self._cards:
                        self._cards.remove(card)
                    elif "JC" in self._cards:
                        self._cards.remove("JC")
                    elif "JD" in self._cards:
                        self._cards.remove("JD")
                    cardID = data.get("x")+'_'+data.get("y")+"_"+card
                    newCard = gameRoom['deck'].pop()
                    self._cards.append(newCard)
                    for connection in gameRoom['members']:
                        connection.write_message({'messageType': 'occupy',
                                                  'cardID': cardID,
                                                  'teamName': self._team})
                    self._nextMemberTurn(gameID)
                if data.get('messageType') == "free" and self._turn:
                    card = data.get("card")
                    if "JH" in self._cards:
                        self._cards.remove("JH")
                    elif "JS" in self._cards:
                        self._cards.remove("JS")
                    cardID = data.get("x")+'_'+data.get("y")+"_"+card
                    newCard = gameRoom['deck'].pop()
                    self._cards.append(newCard)
                    for connection in gameRoom['members']:
                        connection.write_message({'messageType': 'free',
                                                  'cardID': cardID,
                                                  'teamName': self._team})
                    self._nextMemberTurn(gameID)
# |-----------------------------------------------------------------------------|
# _nextMemberTurn :-
# |-----------------------------------------------------------------------------|

    def _nextMemberTurn(self, gameID):
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
        self.write_message({"messageType": 'newCard',
                            "cards": self._cards})
        for member in self._ROOMCONNECTIONS[gameID]['members']:
            member.write_message({'messageType': 'turn',
                                  'memberid': turnID,
                                  'teamName': teamName})

# |--------------------------End of _nextMemberTurn--------------------------------|

    def on_close(self):
        for chatID, connectionBlock in self._ROOMCONNECTIONS.items():
            if self in connectionBlock['members']:
                self._ROOMCONNECTIONS[chatID]['members'].remove(self)
                self._ROOMCONNECTIONS[chatID]['game'] = False
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

# ===============================================================================
# Chat- Main page to connect chat rooms
# ===============================================================================


class Play(MainHandler):
    def get(self):
        self.render("sources/gameRoom.html")


if __name__ == "__main__":
    import os
    deck = os.listdir("sources/images/FrontDeck")
    for card in deck:
        print("'{}'".format(card.split(".")[0]))
