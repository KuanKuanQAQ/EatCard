# -*- coding: utf-8 -*-  
import json
import socket
import argparse
from queue import Queue
from threading import Thread, Condition

from game import Game

class sockServer(object):
    def __init__(self):
        self._client_queue = Queue()
        self._card_queue = Queue()
        self._name2card = {}
        self._client_name2sock = {}
        self._client_sock2name = {}
        self.thread_cnt = 0

    def init(self, host='', post=10021):
        # Run the erver
        sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((host, post))
        sock.listen(5)
        self._nplayer = int(input('input the # of players...\n'))
        for i in range(self._nplayer):
            t = Thread(target=self.inst_client)
            t.daemon = True
            t.start()
        t = Thread(target=self.read_card)
        t.daemon = True
        t.start()
        print("server runing......")
        client_name_poisx = "player"
        index = 1
        while True:
            client_sock, client_addr = sock.accept()
            client_name = client_name_poisx + str(index)
            index += 1
            self._client_name2sock[client_name] = client_sock
            self._client_sock2name[client_sock] = client_name
            self._client_queue.put((client_sock, client_addr))

    def inst_client(self):
        sock, client_addr = self._client_queue.get()
        print('connection begin:', client_addr)
        self.sendall(str(self._client_sock2name[sock])+' enter server.')
        self.thread_cnt += 1
        if self.thread_cnt == self._nplayer:
            self.sendall('all players are ready.')
            self.game_board = Game(self._nplayer, self._client_name2sock)
            self.send_game()
        read_thread = Thread(target = self.read, args = (sock, ))
        read_thread.daemon = True
        read_thread.start()

        while True:
            if not read_thread.is_alive():
                break
        client_name = self._client_sock2name[sock]
        del self._client_sock2name[sock]
        del self._client_name2sock[client_name]
        print('connection closed:', client_addr)
        self.thread_cnt -= 1

        t = Thread(target=self.inst_client)
        t.daemon = True
        t.start()

    def read(self, sock):
        while True:
            message = sock.recv(1024).decode()
            if message == '':
                break
            client_name = self._client_sock2name[sock]
            if message[:3] == '-p ':
                self._card_queue.put((client_name, int(message[3:])))
            else:
                self.sendall(message, from_name=client_name)

    def read_card(self):
        played_cards_num = 0
        while True:
            player_name, player_card = self._card_queue.get()
            if player_card in self.game_board.player2hand[player_name]:
                if player_name in self._name2card:
                    client_sock = self._client_name2sock[player_name]
                    message = ('I' + '|' + 'sys' + ': ' + 'you have played card ' + str(self._name2card[player_name]) + '.')
                    print(message+'('+player_name+')')
                    message = message.encode()
                    client_sock.sendall(message)
                else:
                    client_sock = self._client_name2sock[player_name]
                    message = ('I' + '|' + 'sys' + ': ' + 'you play card ' + str(player_card) + '.')
                    print(message+'('+player_name+')')
                    message = message.encode()
                    client_sock.sendall(message)
                    self._name2card[player_name] = player_card
                    if len(self._name2card) == self._nplayer:
                        name2card = json.dumps(self._name2card)
                        self.sendall('play card list: '+name2card, to_field='INFO')
                        self.game_board.play(self._name2card)

                        self.send_game()
                        self._name2card = {}
                        self._card_queue = Queue()
                        played_cards_num += 1

                        if max(self.game_board.player2score.values()) >= 66:
                            if sorted(self.game_board.player2score.values())[-1] == sorted(self.game_board.player2score.values())[-2]:
                                self.sendall('it is a draw.')
                            else:
                                for player in self.game_board.player2score:
                                    if self.game_board.player2score[player] == max(self.game_board.player2score.values()):
                                        loser = player
                                        break
                                self.sendall('loser is: '+loser)
            else:
                client_sock = self._client_name2sock[player_name]
                message = ('I' + '|' + 'sys' + ': ' + 'you do not have card ' + str(player_card) + '.')
                print(message+'('+player_name+')')
                message = message.encode()
                client_sock.sendall(message)
            # Reset game
            if played_cards_num == 10 * self._nplayer:
                self.sendall('start the next round.')
                self.game_board = Game(self._nplayer, self._client_name2sock, name2score=self.game_board.player2score)
                self.send_game()
                played_cards_num = 0


    def send_game(self):
        player2hand = json.dumps(self.game_board.player2hand)
        player2score = json.dumps(self.game_board.player2score)
        line2desk = json.dumps(self.game_board.line2desk)
        self.sendall(player2score, to_field='SCORE')
        self.sendall(line2desk, to_field='DESK')
        
        for client_name in self._client_name2sock:
            client_sock = self._client_name2sock[client_name]
            message = json.dumps(self.game_board.player2hand[client_name])
            message = ('H' + '|' + 'sys' + ': ' + str(message))
            print(message+' ('+client_name+')')
            message = message.encode()
            client_sock.sendall(message)

    def sendall(self, message, from_name='sys', to_field='INFO'):
        field_dict = {'INFO':'F', 'DESK':'D', 'HAND':'H', 'SCORE':'S', 'INPUT':'I'}
        message = field_dict[to_field] + '|' + str(from_name) + ': ' + str(message)
        print(message)
        message = message.encode()
        for client_sock in self._client_name2sock.values():
            client_sock.sendall(message)
        
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', type=str, default='')
    parser.add_argument('--post', type=int, default=15961)
    args = parser.parse_known_args()[0]

    server = sockServer()
    server.init(args.host, args.post)