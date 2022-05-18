# -*- coding: utf-8 -*-  
import random

class Game(object):
    def __init__(self, player_num, name2sock, card_num=104, line_num=5):
        assert player_num < 10, 'too many players'
        assert player_num == len(name2sock), 'fatal error'
        player_num2card_num = {2:64, 3:84, 4:84, 5:84, 6:84, 7:104, 8:104, 9:104}
        
        self.player_num = player_num
        self.card_num = player_num2card_num[player_num]
        self.line_num = line_num
        print('*'*10)
        print('player_num:', self.player_num)
        print('card_num:', self.card_num)
        print('line_num:', self.line_num)
        print('*'*10)
        
        self.player_name = [i for i in name2sock]
        self.player2score = {}
        self.player2hand = {}
        self.line2desk = {}
        self.draw_card()
        
    def draw_card(self):
        shuffle_card = list(range(1,self.card_num+1))
        random.shuffle(shuffle_card)
        for i, name in enumerate(self.player_name):
            self.player2score[name] = 0
            self.player2hand[name] = sorted(shuffle_card[i * 10: i * 10 + 10])
        for i in range(self.line_num):
            self.line2desk[i] = [shuffle_card[self.player_num * 10 + i]]

    def play(self, player2card):
        for i in self.player_name:
            self.player2hand[i].remove(player2card[i])
        player2card = dict(sorted(player2card.items(), key = lambda kv:(kv[1], kv[0])))
        #print(player2card)
        for i in player2card:
            insert_card = player2card[i]
            desk_min = min([self.line2desk[line][-1] for line in self.line2desk])
            if insert_card < desk_min:
                #吃掉最小尾牌行
                for line in self.line2desk:
                    if self.line2desk[line][-1] == desk_min:
                        self.player2score[i] += self.cal_score(self.line2desk[line])
                        self.line2desk[line][0] = insert_card
                        self.line2desk[line] = self.line2desk[line][:1]
                        break
            else:
                #插在尾牌最接近且小于insert_card行的末尾
                min_gap = insert_card - desk_min
                for line in self.line2desk:
                    if self.line2desk[line][-1] < insert_card:
                        min_gap = min(insert_card - self.line2desk[line][-1], min_gap)
                for line in self.line2desk:
                    if min_gap == insert_card - self.line2desk[line][-1]:
                        self.line2desk[line].append(insert_card)
                        if (len(self.line2desk[line]) > 5):
                            self.player2score[i] += self.cal_score(self.line2desk[line][:5])
                            self.line2desk[line][0] = self.line2desk[line][5]
                            self.line2desk[line] = self.line2desk[line][:1]
                        break
            #print(self.line2desk)
            #print(self.player2score)
    
    def cal_score(self, card_list):
        ans = 0
        for i in card_list:
            if i % 11 == 0:
                ans += 5
            elif i % 10 == 0:
                ans += 3
            elif i % 5 == 0:
                ans += 2
            else:
                ans += 1
        return ans

        
if __name__ == '__main__':
    g = Game(3, ['player1', 'player2', 'player3'])
    g.play({'player1':12, 'player2':13, 'player3':99})
    g.play({'player1':10, 'player2':14, 'player3':5 })
    g.play({'player1':98, 'player2':1,  'player3':7 })


        
