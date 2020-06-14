from pprint import pprint
import numpy as np
from skimage import measure
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
occupied = {'1': [(1, 0), (2, 0), (3, 0),  (5, 1), (4, 0), (6, 8), (3, 3), (9, 9)],
            # '2': [(2, 2),  (4, 4), (3, 3), (6, 6), (1, 1)],
            # '2': [(7, 1), (4, 1), (5, 2), (3, 0), (6, 3), (2, 0), (2, 9), (2, 1), (2, 4), (7, 4)],
            # '2': [(0, 2), (1, 3), (2, 4), (3, 5), (4, 6)],
            # '2': [(9, 0), (8, 1), (7, 2), (6, 3), (5, 4)],
            '2': [(1, 5), (7, 9), (6, 9), (0, 8), (0, 6), (3, 3), (3, 6), (4, 9), (8, 9), (5, 0), (8, 5), (9, 3), (7, 5), (1, 4), (5, 9)],
            '3': [(1, 8), (2, 8), (3, 9), (4, 8), (5, 8)]}
teamName = ['1', '2', '3']
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
if __name__ == "__main__":

    for key, values in occupied.items():
        sortedVal = sorted(values, key=lambda k: [k[1], k[0]])
        tempGrid = np.array(grid[:])
        for val in sortedVal:
            tempGrid[val[0]][val[1]] = teamName.index(key)+1
            tempGrid[0][0] = teamName.index(key)+1
            tempGrid[9][9] = teamName.index(key)+1
            tempGrid[0][9] = teamName.index(key)+1
            tempGrid[9][0] = teamName.index(key)+1
        subStr = "".join(5*[str(teamName.index(key)+1)])
        winStreak = []
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
                if d >= 0:
                    for j in range(x, x+5):
                        print(j, d+j)
                else:
                    for j in range(x, x+5):
                        print(abs(d)+j, j)
            if subStr in dialr:
                x = dialr.index(subStr)
                print("DiaLR ", d, x, dialr)
                if d >= 0:
                    for j in range(x-5, x):
                        print(9-j, d+j)
                else:
                    for j in range(x, x+5):
                        print(9-abs(d)+j, j)
            if subStr in row:
                x = row.index(subStr)
                print("Row ", i, x, row)
                for j in range(x, x+5):
                    print(j, i)
                    winStreak.append((j, i))
            if subStr in col:
                x = col.index(subStr)
                print("Col ", i, x, col)
                for j in range(x, x+5):
                    print(i, j)
        winStreak = [str(win[0])+"_"+str(win[1])+"_"+BOARD[win[0]][win[1]]
                     for win in winStreak]
        print(winStreak)
