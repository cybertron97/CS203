import sys

bht_index_size = 8
STATE_TABLE = [[[0, 1],
                [0, 1]],
               [[0, 2], 
                [3, 1], 
                [0, 1], 
                [0, 1]]]

def getArguments():
    if(len(sys.argv) != 3):
        print('Error: BranchSim.py <tracefile> (<m_value>,<n_value>)\n')
        sys.exit(1)
    filename = sys.argv[1]
    (m,n) = sys.argv[2].replace('(','').replace(')','').split(',')
    m = int(m)
    n = int(n)
    if(m < 0 or n < 1 or n > 2):
        print('Error: (m,n) value is not accepted, m > 0 and n = 1 or 2')
        sys.exit(1)
    return filename, m, n

def readFile(filename):
    accesses = []
    with open(filename, 'r') as file:
        for line in file:
            (addr, actual) = line.split(" ")
            accesses.append([int(addr,16), getStateNumber(actual.replace("\n", "")), -1])
    return accesses

def countMisPredictions(accesses, m, n):
    gbh = initializeGlobalHistory(m)
    last_pred = 0
    curr_state = 0
    mispredictions = 0
    gbc = 0
    for i in range(0, len(accesses)):
        if m == 0 and n == 1:
            accesses[i][2] = last_pred
            last_pred = accesses[i][1]
        elif m == 0 and n == 2: 
            curr_state = getNextState(curr_state, accesses[i][1], n)
            accesses[i][2] = curr_state
        else:
            curr_state = getGHPrediction(accesses[i], gbh, gbc)
            if curr_state == -1:
                curr_state = 0
            accesses[i][2] = curr_state
            pred = curr_state
            last_state = curr_state
            curr_state = getNextState(curr_state, accesses[i][1], n)
            gbh, gbc = updateGlobalHistory(accesses[i], gbh, gbc, curr_state, accesses[i][1], m)
        if(accesses[i][1] != isTaken(accesses[i][2])):
            mispredictions = mispredictions + 1
    count = 0
    for i in range(len(gbh)):
        for j in range(len(gbh[0])):
            if(gbh[i][j] != -1):
                count = count + 1
    return mispredictions, count

def getNextState(state, pred, n):
    global STATE_TABLE
    return STATE_TABLE[n-1][state][pred]

def getStateNumber(taken):
    if taken == 'N':
        return 0
    elif taken == 'T':
        return 1
    elif taken == 'NT':
        return 2
    else:
        return 3
        
def isTaken(taken):
    if taken == 0 or taken == 2:
        return 0
    else:
        return 1

def initializeGlobalHistory(m):
   if m == 0:
       return []
   else:
       global bht_index_size
       gbh = [[-1 for j in range(2**m)] for i in range (2**bht_index_size)]
       return gbh

def getGHPrediction(access, gbh, gbc):
    global bht_index_size
    bht_index = access[0] & ((2 ** bht_index_size) - 1)
    return gbh[bht_index][gbc]

def updateGlobalHistory(access, gbh, gbc, pred, expected, m):
    global bht_index_size
    bht_index = access[0] & ((2 ** bht_index_size) - 1)
    gbh[bht_index][gbc] = pred
    return gbh, ((gbc << 1) | isTaken(expected)) & ((2 ** m) - 1)

if __name__ == "__main__":
   fname, m, n = getArguments()
   accesses = readFile(fname)
   misses, count = countMisPredictions(accesses, m, n)
   print("Count Of Utilized Entries: ", count)
   print("Number of Accesses: ", len(accesses))
   print("Number of Mispredictions: ", misses)