import scipy
import socket	
import numpy as np		 
import pickle
import curses
import random
import time
import threading
import sys
s = socket.socket()		 
port = int(sys.argv[2])
print(sys.argv[1])
s.connect((sys.argv[1], port)) 
print("Starting game")
connectmsg = s.recv(1024) 
connectmsg = pickle.loads(connectmsg)
print(connectmsg)
symbol =  int(connectmsg)+1
print("Loading")
time.sleep(3)
screen = curses.initscr()
curses.curs_set(0)
    
w = curses.newwin(35, 35, 0, 0)
def render(socket,w):
    global endprog,win
    win = False
    endprog = False
    while True:
        try:

            lst = socket.recv(100*1024)
            # time.sleep(0.05)
            lst = pickle.loads(lst)
            snake1 = lst[1]
            symbol = lst[0]
            win = lst[2]
            if win == True:
                w.clear()
                curses.endwin()        
                print("You win")
                endprog = True
                quit()
        
            

            if snake1[0][0] == -1:
                endprog = True
                
            
                return 
                
            else:
                if win == "Full":
                    w.addch(snake1[0][0], snake1[0][1], 'h')
                    w.addch(snake1[1][0], snake1[1][1], symbol)
                    w.addch(snake1[2][0], snake1[2][1], symbol)
                    continue

                
                w.addch(snake1[0][0], snake1[0][1], symbol)
                tail = snake1.pop()
                w.addch(tail[0], tail[1], ' ')
        except OSError as err:
            continue
        except pickle.UnpicklingError as err:
            continue    



def MoveValidation(s,w):

    


    global endprog
    endprog = False 
    
    w.keypad(1)
    w.timeout(100)

    while endprog == False:
        
        w.border('|', '|', '-', '-', '+', '+', '+', '+')
        move = w.getch()
        if move!= -1:
            check = True
            if move == curses.KEY_DOWN:
                move = "s"
                check = False
            if move == curses.KEY_UP:
                move = "w"
                check = False
            if move == curses.KEY_LEFT:
                move = "a"
                check = False
            if move == curses.KEY_RIGHT:
                move = "d"
                check = False
            if check == False:
                if endprog == False:
                    s.send(pickle.dumps(move))
                else:
                    break
    
    
    w.clear()
    curses.endwin()
    if win == True:
        print("YOU WIN!!!!")
    else:

        print("You lose")
    
t1 = threading.Thread(target=MoveValidation, args=(s,w,)) 
t2 = threading.Thread(target=render, args=(s,w,)) 
t2.start()  
t1.start()      
t1.join()
t2.join() 
s.close()	 
