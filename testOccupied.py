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
occupied = {'1': [(1, 0), (2, 0), (3, 0),  (5, 1), (4, 0), (6, 6), (3, 3), (9, 9)],
            '2': [(2, 2),  (4, 4), (3, 3), (6, 6), (1, 1)],
            # '2': [(4, 3),  (5, 4), (6, 3), (7, 2), (8, 1)],
            '3': [(1, 8), (2, 8), (3, 8), (4, 8), (5, 8)]}
teamName = ['1', '2', '3']

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
        for i in range(10):
            # for j in range(6):
            dia = "".join([str(v) for v in tempGrid.diagonal(i-5)])
            dialr = "".join([str(v)
                             for v in np.fliplr(tempGrid).diagonal(i-5)])
            col = "".join([str(v) for v in tempGrid[i, :]])
            row = "".join([str(v) for v in tempGrid[:, i]])
            # print(dia, row, col)
            if subStr in dia:
                x = dia.index(subStr)
                print("Dia ", i, x, dia)
                for j in range(x, x+5):
                    print((i-5)+j, j)
            if subStr in dialr:
                x = dialr.index(subStr)
                print("DiaLR ", i, x, dialr)
                for j in range(x, x+5):
                    print(j, 9-((i-5)+j))
            if subStr in row:
                x = row.index(subStr)
                print("Row ", i, x, row)
                for j in range(x, x+5):
                    print(j, i)
            if subStr in col:
                x = col.index(subStr)
                print("Col ", i, x, col)
                for j in range(x, x+5):
                    print(i, j)
