import curses, time
import numpy as np
import matplotlib.pyplot as plt

def primesfrom2to(n): #Prime number generator for hash
    #Code from
    #https://stackoverflow.com/questions/2068372/fastest-way-to-list-all-primes-below-n/3035188#3035188
    """ Input n>=6, Returns a array of primes, 2 <= p < n """
    sieve = np.ones(n//3 + (n%6==2), dtype=np.bool)
    for i in range(1,int(n**0.5)//3+1):
        if sieve[i]:
            k=3*i+1|1
            sieve[       k*k//3     ::2*k] = False
            sieve[k*(k-2*(i&1)+4)//3::2*k] = False
    return np.r_[2,3,((3*np.nonzero(sieve)[0][1:]+1)|1)]

def init(params):
    params["block_length"] = 0
    params["x_blocks"] = 20
    params["y_blocks"] = 20
    params["x_size"] = (params["block_length"]+1)*params["x_blocks"] + 1
    params["y_size"] = (params["block_length"]+1)*params["y_blocks"] + 1
    params["window_size"] = 5
    params["cursors"] = [">", "∧", "<", "v"] #right, up, left, down
    params["print"] = 1

    #Randomize start position
    params["posx"] = 0#int(np.random.randint(params["x_blocks"]))
    params["posy"] = 0#int(np.random.randint(params["y_blocks"]))
    params["cursor"] = ">"

    #Top/bottom of board etc.
    params["max_left"] = params["posx"]
    params["max_right"] = params["posx"]
    params["max_up"] = params["posy"]
    params["max_down"] = params["posy"]
    params["coverage_board"] = np.zeros([params["x_size"], params["y_size"]])

    params["delta"] = 0.01
    params["epsilon"] = 0.05
    params["x_size_guess"] = 0
    params["y_size_guess"] = 0
    params["num_loops"] = 0
    params["data_true_coverage"] = []
    params["data_exp_coverage"] = []


    n = int(np.round((params["x_blocks"]+1)*(params["y_blocks"]+1)/7.5))
    h_n = np.sum([1/(n-i) for i in range(0, n)])
    params["ex"] = np.zeros(n)
    for m in range(n):
        h_nmm = np.sum([1/(n-i) for i in range(0, n-m)])
        params["ex"][m] = n*(h_n - h_nmm)
    params["ex"] = np.flip(params["ex"][-1] - params["ex"])

def create_board(block_length, params):
    board = []
    bl = params["block_length"]
    for y in range(params["y_size"]):
        temp_row = []
        for x in range(params["x_size"]):
            if   (y % (bl + 1) == 0):
                temp_row.append("-")
            elif (y % (bl + 1) == 1) or (y % (bl + 1) == bl):
                if   (x % (bl + 1) == 0):
                    temp_row.append("-")
                elif (x % (bl + 1) == 1):
                    temp_row.append("x")
                elif (x % (bl + 1) == bl):
                    temp_row.append("x")
                else:
                    temp_row.append("x")
            else:
                if   (x % (bl + 1) == 0):
                    temp_row.append("-")
                elif (x % (bl + 1) == 1):
                    temp_row.append("x")
                elif (x % (bl + 1) == bl):
                    temp_row.append("x")
                else:
                    temp_row.append(" ")
        board.append(temp_row)

    return board

def utils(board, params):
    x = params["posx"]
    y = params["posy"]
    if x < params["max_left"]: params["max_left"] = x
    if x > params["max_right"]: params["max_right"] = x
    if y < params["max_up"]: params["max_up"] = y
    if y > params["max_down"]: params["max_down"] = y

    if params["print"] == 1:
        row = "Leftmost: " + str(params["max_left"]) + "; "
        row += "Rightmost: " + str(params["max_right"]) + "; "
        row += "Upmost: " + str(params["max_up"]) + "; "
        row += "Downmost: " + str(params["max_down"]) + "."
        win.addstr((2*params["window_size"]+3),0,row)
    params["x_size_guess"] = (params["max_right"] - params["max_left"])/(params["block_length"] + 1)
    params["y_size_guess"] = (params["max_down"] - params["max_up"])/(params["block_length"] + 1)

    #checking coverage of board
    params["coverage_board"][x][y] = 1
    params["coverage"] = np.int32(np.sum(params["coverage_board"]))
    tru_cov = params["coverage"]/((params["x_blocks"]+1)*(params["y_blocks"]+1))
    if params["print"] == 1:
        row = "True Coverage: " + str(tru_cov)
        win.addstr((2*params["window_size"]),0,"    "+row + "                   ")

    idx = (np.abs(params["ex"] - params["num_loops"])).argmin()
    exp_cov = (idx+1)/(len(params["ex"]))
    if params["print"] == 1:
        win.addstr((2*params["window_size"]+1),0,"Expected coverage: "+str(exp_cov) + "             ")
        win.addstr((2*params["window_size"]+2),0,"Num loops: " + str(params["num_loops"]))

    params["data_true_coverage"].append(tru_cov)
    params["data_exp_coverage"].append(exp_cov)

def setup_hash(params):

    p_list = []#array containing all the valid primes for a certain universe size
    nele = (params["x_size_guess"]+5)*(params["y_size_guess"]+5)
    p_ = primesfrom2to(10*nele)
    min = nele;
    max = 10*nele;
    for prime in p_:
        if (prime > min and prime < max):
            p_list.append(prime)

    params["n"] = int(1/params["epsilon"]) #number of bins
    params["i"] = int(np.log(1/params["delta"])+1) #number of hash tables
    params["p"] = np.random.choice(p_list, params["i"], replace=False)

    a = []
    b = []
    for i in range(params["i"]):
        prime = params["p"][i]
        n1 = np.ceil(np.random.uniform()*1000)
        n2 = np.ceil(np.random.uniform()*(prime - 1))
        n3 = np.ceil(np.random.uniform()*1000)
        n4 = np.ceil(np.random.uniform()*(prime - 1))
        a.append(n1*prime + n2)
        b.append(n3*prime + n4)

    params["a"] = a
    params["b"] = b
    params["cms"] = np.zeros([params["i"], params["n"]])

def step_count_min(params):
    x = params["posx"]
    y = params["posy"]
    value = y*params["x_size"] + x
    for i in range(params["i"]):
        ind = int(((params["a"][i]*value + params["b"][i]) % params["p"][i]) % params["n"])
        params["cms"][i, ind] += 1

def run_sim(board, params): #The movement loop

    print_board(board, params)
    for i in range(200000):
        for j in range(params["block_length"] + 1):
            time.sleep(0.01)
            move(board, params)
            if params["print"] == 1: print_board(board, params)

        utils(board, params)
        step_count_min(params)
        if(check_if_loop(params)):
            params["num_loops"] += 1
            params["cms"] -= params["cms"]
            #setup_hash(params) #reset hash table
        if(params["data_exp_coverage"][-1] >= 0.9):
            break;

def print_board(board, params):
    ws = params["window_size"]
    x = params["posx"]
    y = params["posy"]
    xllim = max(0, x - ws)
    xulim = min(x + ws, params["x_size"])
    yllim = max(0, y - ws)
    yulim = min(y + ws, params["y_size"])
    if (xulim == params["x_size"]): xllim = params["x_size"] - 2*ws
    if (yulim == params["y_size"]): yllim = params["y_size"] - 2*ws

    trig = 0
    for i in range(yllim, yllim+2*ws):
        row = ""
        for j in range(xllim, xllim+2*ws):
            if (board[i][j] == ">" or board[i][j] == "v" or board[i][j] == "<" or board[i][j] == "∧"):
                trig = 1
                tx = j
            if j == len(board[i]) - 1: row += board[i][j]; break
            row += board[i][j] + " "

        if(trig):
            win.addstr((i - yllim),0,row[0:2*(tx - xllim)])
            win.addstr((i - yllim),len(row[0:2*(tx - xllim)]), row[2*(tx - xllim)], curses.color_pair(1))
            win.addstr((i - yllim),len(row[0:2*(tx - xllim)])+1,row[2*(tx - xllim)+1:])
            trig = 0
        else:
            win.addstr((i - yllim),0,row)
        win.refresh()

def move(board, params):
    cursor = [">", "∧", "<", "v"] #r, u, l, d
    x = params["posx"]
    y = params["posy"]
    c = board[y][x]
    if x < params["x_size"]-1: r = board[y][x+1]
    else: r = " "
    if y > 0: u = board[y-1][x]
    else: u = " "
    if x > 0: l = board[y][x-1]
    else: l = " "
    if y < params["y_size"]-1: d = board[y+1][x]
    else: d = " "

    PD = {"r":1, "u":1, "l":1 ,"d":1}
    if (c == ">"): PD["l"] = 0 #can't turn around
    elif (c == "∧"): PD["d"] = 0
    elif (c == "<"): PD["r"] = 0
    elif (c == "v"): PD["u"] = 0

    if (r == " " or r == "x"): PD["r"] = 0
    if (u == " " or u == "x"): PD["u"] = 0
    if (l == " " or l == "x"): PD["l"] = 0
    if (d == " " or d == "x"): PD["d"] = 0

    subPD = {}
    count = 0
    if PD["r"]:
        subPD[count] = "r"
        count += 1
    if PD["u"]:
        subPD[count] = "u"
        count += 1
    if PD["l"]:
        subPD[count] = "l"
        count += 1
    if PD["d"]:
        subPD[count] = "d"
        count += 1
    dir =  subPD[np.random.randint(0, count)]

    board[params["posy"]][params["posx"]] = "-"
    if dir == "r":
        params["posx"] += 1
        board[params["posy"]][params["posx"]] = ">"
    elif dir == "u":
        params["posy"] -= 1
        board[params["posy"]][params["posx"]] = "∧"
    elif dir == "l":
        params["posx"] -= 1
        board[params["posy"]][params["posx"]] = "<"
    elif dir == "d":
        params["posy"] += 1
        board[params["posy"]][params["posx"]] = "v"

def testmove(board, params):
    for i in range(params["x_size"]-1):
        time.sleep(0.2)
        move1(board, params)
        print_board(board, params)
    for i in range(params["y_size"]-1):
        time.sleep(0.2)
        move2(board, params)
        print_board(board, params)
    for i in range(params["x_size"]-1):
        time.sleep(0.2)
        move3(board, params)
        print_board(board, params)
    for i in range(params["y_size"]-1):
        time.sleep(0.2)
        move4(board, params)
        print_board(board, params)

def check_if_loop(params):
    temp = np.copy(params["cms"])

    x = params["posx"]
    y = params["posy"]
    value = y*params["x_size"] + x

    min_hash = 5
    for i in range(params["i"]):
        ind = int(((params["a"][i]*value + params["b"][i]) % params["p"][i]) % params["n"])
        if params["cms"][i, ind] < min_hash:
            min_hash = params["cms"][i, ind]
    if min_hash >= 2:
        return 1
    return 0

def fig1(params):
    plt.figure()
    plt.plot(np.arange(len(params["data_true_coverage"])), params["data_true_coverage"], label="True")
    plt.plot(np.arange(len(params["data_exp_coverage"])), params["data_exp_coverage"], label="Expected")
    plt.legend()
    plt.xlabel("Steps in Random Walk")
    plt.ylabel("Proportion of Map Covered")
    plt.show()

def printdata(params):
    print("\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n")
    print(params["data_exp_coverage"][-1])
    print(params["data_true_coverage"][-1])
    print(len(params["data_exp_coverage"]))

params = {}
init(params)
setup_hash(params)
board = create_board(params["block_length"], params)
board[params["posy"]][params["posx"]] = params["cursor"]

win = curses.initscr() #Opening window, apply some settings
curses.noecho() #Turn off printing keys out
curses.cbreak() #Turn off enter for keys
curses.start_color()
curses.use_default_colors()
curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_MAGENTA) #drone character color


win.addstr(0,0,"Press any key to start - ")
win.refresh()
win.getch() #Pause for key enter
win.addstr(0,0,"                         ")

run_sim(board, params)
time.sleep(3)

curses.endwin() #End window
