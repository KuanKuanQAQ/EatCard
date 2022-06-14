# -*- coding: utf-8 -*-  
import json
import curses
import argparse
from threading import Thread
from socket import socket, AF_INET, SOCK_STREAM

class sockClient(object):
    def __init__(self):
        self._sock = None
        self._print_index = 4
        self._message_queue_len = 25
        self._desk_index = self._print_index + self._message_queue_len + 2
        self._desk_len = 5
        self._hand_index = self._desk_index + self._desk_len + 2
        self._hand_len = 1
        self._score_index = self._hand_index + self._hand_len + 2
        self._score_len = 1
        self._input_index = self._score_index + self._score_len + 2
        self._message_queue = []
        self._last_desk = None

    def init(self, host="localhost", post=15961):
        self.connect(host, post)
        self._stdscr = curses.initscr()
        self.set_win()
        self._stdscr.addstr(1, 0, 'EAT CARDS by KuanKuan\n', curses.color_pair(3))
        self._stdscr.addstr(self._print_index-1, 0, 'INFO', curses.color_pair(2))
        self._stdscr.addstr(self._desk_index-1, 0, 'DESK', curses.color_pair(2))
        self._stdscr.addstr(self._desk_index-1, 40, 'LAST', curses.color_pair(2))
        self._stdscr.addstr(self._hand_index-1, 0, 'HAND', curses.color_pair(2))
        self._stdscr.addstr(self._score_index-1, 0, 'SCORE', curses.color_pair(2))
        self._stdscr.addstr(self._input_index-1, 0, 'INPUT', curses.color_pair(2))
        self._stdscr.addstr(self._input_index, 0, "ME: ", curses.color_pair(1))
        self._stdscr.refresh()

    def close(self):
        self.unset_win()
        self._sock.close()

    def running(self):
        input_thread = Thread(target = self.input)
        input_thread.daemon = True
        input_thread.start()

        print_thread = Thread(target = self.print_message)
        print_thread.daemon = True
        print_thread.start()
        
        while True:
            if not input_thread.is_alive() or not print_thread.is_alive():
                break

    def set_win(self):
        '''控制台设置'''
        #使用颜色首先需要调用这个方法
        curses.start_color()
        #文字和背景色设置，设置了两个color pair，分别为1和2
        curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        #关闭屏幕回显
        #设置nodelay，使得控制台可以以非阻塞的方式接受控制台输入，超时1秒
        self._stdscr.nodelay(1)
    
    def unset_win(self):
        '''控制台重置'''
        curses.echo()
        #结束窗口
        curses.endwin()

    def print_message(self):
        while True:
            # 堵塞
            messages = self._sock.recv(1024).decode()
            if not messages:
                break
            message_list = messages.split('|')
            for mp, message in enumerate(message_list[1:]):
                message_field = message_list[mp][-1]
                if mp != len(message_list) - 2:
                    message = message[:-1]
                self.print_format(message_field, message)
                self._stdscr.addstr(self._input_index, 0, "ME: ", curses.color_pair(1))
                self._stdscr.refresh()

    def print_format(self, message_field, message):
        if message_field == 'F':    
            if len(self._message_queue) >= self._message_queue_len:
                self._message_queue.pop(0)
            self._message_queue.append(message)
            for i in range(len(self._message_queue)):
                index = i + self._print_index
                m = self._message_queue[i]
                self._stdscr.addstr(index, 3, ' '*100, curses.color_pair(1))
                self._stdscr.addstr(index, 3, m, curses.color_pair(1))
        if message_field == 'D':
            message = message[5:]
            json_obj = json.loads(message)
            for i, line in enumerate(json_obj):
                index = i + self._desk_index
                m = str(json_obj[line])[1:-1]
                self._stdscr.addstr(index, 3, ' '*100, curses.color_pair(1))
                self._stdscr.addstr(index, 3, m, curses.color_pair(1))
            if self._last_desk:
                for i, line in enumerate(self._last_desk):
                    index = i + self._desk_index
                    m = str(self._last_desk[line])[1:-1]
                    self._stdscr.addstr(index, 43, ' '*50, curses.color_pair(1))
                    self._stdscr.addstr(index, 43, m, curses.color_pair(1))
            self._last_desk = json_obj
        if message_field == 'H':
            message = message[5:]
            json_obj = json.loads(message)
            m = str(json_obj)[1:-1]
            self._stdscr.addstr(self._hand_index, 3, ' '*100, curses.color_pair(1))
            self._stdscr.addstr(self._hand_index, 3, m, curses.color_pair(1))
        if message_field == 'S':
            message = message[5:]
            json_obj = json.loads(message)
            m = str(json_obj)[1:-1]
            self._stdscr.addstr(self._score_index, 3, ' '*100, curses.color_pair(1))
            self._stdscr.addstr(self._score_index, 3, m, curses.color_pair(1))
        if message_field == 'I':
            m = message
            self._stdscr.addstr(self._input_index+1, 3, ' '*100, curses.color_pair(1))
            self._stdscr.addstr(self._input_index+1, 3, m, curses.color_pair(1))

    def input(self):
        self._stdscr.nodelay(0)
        while True:
            s = self._stdscr.getstr(self._input_index, 4)
            self._stdscr.addstr(self._input_index, 4, " "*100, curses.color_pair(1))
            if s == b"":
                break
            self._sock.sendall(s)
        self._stdscr.nodelay(1)

    def connect(self, host, post):
        sock = socket(AF_INET, SOCK_STREAM)
        sock.connect((host, post))
        self._sock = sock


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', type=str, default='114.116.102.182')
    parser.add_argument('--post', type=int, default=15961)
    args = parser.parse_known_args()[0]
    
    client = sockClient()
    # init
    client.init(args.host, args.post)

    # run Loop
    try:
        client.running()
    except Exception:
        pass
    # close
    finally:
        client.close()
