import scipy
import socket	
import numpy
import pickle
import curses
import random
import threading
import time
import queue 
import sys

def nextkeygen(socket, id,np):
    socket.setblocking(0)
    global keychange,next_key,moveq, movearray,gameover
    movearray = []
    for i in range(np):
        i = i
        movearray.append("")
    
    moveq =  queue.Queue(maxsize=0)
    gameover = True
    while (gameover==True):
        try:
            data = socket.recv(1024*10)
            data = pickle.loads(data)
            if data in ["s","a","w","d"]:
                next_key = data
                keychange = True
                # moveq.put((next_key,id))
                movearray[id] = data

            else:
                next_key = -1
                keychange = False
            
        except OSError as err:
            continue
        

s = socket.socket()		 
print ("Socket successfully created")
port = int(sys.argv[2])
s.bind((sys.argv[1], port))		 
print ("socket binded to =" ,port)
s.listen(5)	 
print ("socket is listening")			
sh,sw = 0,0  
counter  = 0
nplayers = int(sys.argv[3])
playsoclist = [] #Sockets of Players
while len(playsoclist) < nplayers:
        
        c, addr = s.accept()	 
        print(c)
        print ('Got connection from', addr)
        playsoclist.append(c)
        if len(playsoclist) > 0: 
            output = str(len(playsoclist))
            c.send(pickle.dumps(output))
            
        

sh=35
sw=35
              
snk_x = sw//2
snk_y = sh//2
def gensnakes(tup):
    if tup[2] ==1:
        snk_y = tup[1]
        snk_x = tup[0]
        snake = [[snk_y, snk_x],[snk_y, snk_x-1],[snk_y, snk_x-2]]
        return snake
    else:
        snk_y = tup[1]
        snk_x = tup[0]
        snake = [[snk_y, snk_x],[snk_y-1, snk_x],[snk_y-2, snk_x]]
        return snake


def gameobjgen(x,y,nplayers):
    headcord =[]
    gameobjectlist = []
    while True:
        if len(headcord) == nplayers:
            break
        n_x = numpy.random.randint(5,x)
        n_y = numpy.random.randint(5,y)
        xory = numpy.random.randint(1,3)
        if (n_x,n_y,xory) in headcord:
            continue
        else:
            headcord.append((n_x,n_y,xory))
    for item in headcord:
        temp = gensnakes(item)
        gameobjectlist.append(temp)
    return gameobjectlist




    

# snake1 = [
#     [snk_y, snk_x],
#     [snk_y, snk_x-1],
#     [snk_y, snk_x-2]
# ]
# snake2 = [
#     [snk_y, snk_x-5],
#     [snk_y, snk_x-6],
#     [snk_y, snk_x-7]
# ]

# snake3 = [
#     [snk_y+9, snk_x],
#     [snk_y+10, snk_x],
#     [snk_y+11, snk_x]
# ]
gameobjects = gameobjgen(23,23,nplayers)
# gameobjects.append(snake1)
# gameobjects.append(snake2)
# gameobjects.append(snake3)
heads  = []
for i in range(len(gameobjects)):
    heads.append([gameobjects[i][0][0],gameobjects[i][0][1]])
# heads.append([snake2[0][0],snake2[0][1]])
# heads.append([snake3[0][0],snake3[0][1]])
def collision(head,gameobjs,pid):
    for i in range(len(gameobjs)):
        if head in gameobjs[i][1:]:
            if pid == i:
                continue
            return i
    return -1        

# Game loop        
def Gameloop(key,playsoclist,pid,snake1,heads,gameobjects,np):
    global keychange,next_key,moveq,headlist,snakeobj, movearray,rPlayers,gameover
    gameover = True
    rPlayers = np
    movearray = []
    for i in range(np):
        movearray.append("")
    
    headlist = heads
    snakeobj = gameobjects
    moveq =  queue.Queue(maxsize=0)
    keychange = False
    next_key = -1
    # mc = 0
    while gameover==True:
        
        if movearray[pid] != "":
            key = movearray[pid]
            movearray[pid] =""
            print("Key = ", key )
            
        new_head1 = [snake1[0][0],snake1[0][1]]
        
        if key == "s":
            new_head1[0] += 1
        if key == "w":
            new_head1[0] -= 1
        if key == "a":
            new_head1[1] -= 1
        if key == "d":
            new_head1[1] += 1
        if key == "x":
            for i in range(len(playsoclist)):
                if playsoclist[i] != " ":
                    finallist= (str(pid+1),snake1,"Full")
                    # print(finallist)
                    playsoclist[i].send(pickle.dumps(finallist))
            continue
        if headlist[pid] == [-1,-1]:
            break
        snake1.insert(0, new_head1)
        if snake1[0][0] in [0, sh] or snake1[0][1]  in [0, sw] or new_head1 in headlist:
            print("End")
            fail = [[-1,-1]]
            if playsoclist[pid] == " ":
                break
            playsoclist[pid].send(pickle.dumps((str(pid),fail,False)))
            playsoclist[pid].close()
            playsoclist[pid] = " "
            rPlayers -=1
            if new_head1 in headlist:
                print("HEAD TO HEAD")
                nPID = headlist.index(new_head1)
                playsoclist[nPID].send(pickle.dumps((str(nPID),fail,False)))
                playsoclist[nPID].close()
                playsoclist[nPID] = " "
                headlist[pid] = [-1,-1]
                headlist[nPID] = [-1,-1]
                rPlayers-=1
                if rPlayers==0:
                   print("ALL LOSE")
                   gameover = False
                   quit() 
                if rPlayers == 1:
                    for plr in playsoclist:
                        if plr != " ":
                            finallist= (str(pid+1),snake1,True)
                            plr.send(pickle.dumps(finallist))

                
                
            break
        else:
            print("Sending back move", snake1[0], "to ", pid)
            headlist[pid] = new_head1
            rpid = collision(new_head1, snakeobj,pid) 
            if rpid >= 0:
              rPlayers-=1
              fail = [[-1,-1]] 
              print("COLLISION\n\n\n\n")  
              print("Player ", pid+1, " collided with " , rpid+1)    
              headlist[rpid] = [-1,-1]
              snakeobj[rpid] = [[headlist]]
              if playsoclist[rpid] ==" ":
                  continue
              playsoclist[rpid].send(pickle.dumps((str(rpid),fail,False)))
              playsoclist[rpid].close()
              playsoclist[rpid] = " "  
            time.sleep(0.3)
            
            win = False
            if rPlayers ==1:
                win = True
            for i in range(len(playsoclist)):
                if playsoclist[i] != " ":
                    finallist= (str(pid+1),snake1,win)
                    playsoclist[i].send(pickle.dumps(finallist))
                    if win == True:
                        gameover = False
                    
            snake1.pop()
            snakeobj[pid] = snake1
print("Start of game")
threadlist = []
gamestatelist = []
for i in range(nplayers):
    t1 = threading.Thread(target=nextkeygen, args=(playsoclist[i],i,nplayers,)) 
    threadlist.append(t1)
    t2 = threading.Thread(target=Gameloop, args=("x",playsoclist,i,gameobjects[i],heads,gameobjects,nplayers,)) 
    gamestatelist.append(t2)
  
for i in range(nplayers):
    threadlist[i].start()
    gamestatelist[i].start()

for i in range(nplayers):
    threadlist[i].join()
    gamestatelist[i].join()
print("Server out")

t1.join()
t2.join()
c.close()    
s.close()













    