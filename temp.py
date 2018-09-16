import random
rID = 0
randmask = []
for i in range(0,5):    #(1,4):)
    rID += int(random.randint(1, 9)*10**i)
print(rID)