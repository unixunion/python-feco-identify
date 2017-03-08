import numpy as np
from random import shuffle


# accepts a n-dimentional array, and "l" sets which index in each record is the label
# e.g:
# >>> test_array = [
#        [1,1,"ring","gold"],
#        [35,50, 0, "nail","iron"],
#        [25,50, 0, "screw","iron"]]
# >>> d = buildData(test_array, l=3)
# >>> d.target
# [0, 1, 1]
# >>> d = buildData(test_array, l=2)
# >>> d.target
# [0, 1, 2]
class buildData:
    def __init__(self, aray, l=4):

        # create data, target and target_data lists
        self.data = []
        self.target = []
        self.target_data = []

        # iterate over the objects in the array, appending co-ordintates and labeling
        for i in aray:
            self.data.append([i[0], i[1]])

            # check if the "label" value is already present in the target_data list
            if not i[l] in self.target_data:
                self.target_data.append(i[l])
            self.target.append(self.target_data.index(i[l]))

        self.data = np.array(self.data)


# mixed bag of "common" finds using 2 coordinates only
# this should be improved to use 3x 2 coordinates scanned at 3 different angles.
# fe co
class sweden_data:
    def __init__(self, l=4):
        # source data
        self.da = [
            [2, 42,  0, "5kr", "silver coin"],
            [3, 46,  0, "2kr", "silver coin"],
            [5, 47,  0, "2kr", "silver coin"],
            [6, 46,  0, "2kr", "silver coin"],
            [9, 26,  0, "5kr", "silver coin"],
            [9, 38,  0, "50 ore", "silver coin"],
            [10, 28, 0, "wine top", "picnic trash"],
            [11, 4,  0, "10 ore", "silver coin"],
            [11, 20, 0, "pull tab", "picnic trash"],
            [11, 22, 0, "pull tab", "picnic trash"],
            [11, 25, 0, "5kr", "CuNi coin"],
            [11, 46, 0, "2/3 skillning", "copper coin"],
            [11, 46, 0, "1kr", "silver coin"],
            [12, 6,  0, "25 ore", "bronze coin"],
            [12, 17, 0, "1kr", "CuNi coin"],
            [12, 18, 0, "pull tab", "picnic trash"],
            [12, 21, 0, "pull tab", "picnic trash"],
            [12, 22, 0, "pull tab", "picnic trash"],
            [12, 22, 0, "bottle top", "picnic trash"],
            [12, 24, 0, "bottle top", "picnic trash"],
            [12, 24, 0, "pull tab", "picnic trash"],
            [12, 25, 0, "bottle top", "picnic trash"],
            [12, 26, 0, "10 ore", "silver coin"],
            [12, 28, 0, "bottle top", "picnic trash"],
            [12, 28, 0, "1 ore", "copper coin"],
            [12, 28, 0, "wine top", "picnic trash"],
            [12, 31, 0, "wine top", "picnic trash"],
            [12, 32, 0, "25 ore", "silver coin"],
            [12, 34, 0, "2 ore", "copper coin"],
            [12, 38, 0, "2 ore", "copper coin"],
            [12, 39, 0, "bottle top", "picnic trash"],
            [12, 40, 0, "5 ore", "bronze coin"],
            [12, 40, 0, "5 ore", "bronze coin"],
            [12, 40, 0, "10kr", "nordic gold coin"],
            [12, 41, 0, "5 ore", "copper coin"],
            [12, 42, 0, "1kr", "CuNi copper Coin"],
            [12, 42, 0, "5 ore", "bronze coin"],
            [12, 42, 0, "bottle top", "picnic trash"],
            [12, 44, 0, "25 ore", "silver coin"],
            [12, 45, 0, "50 ore", "silver coin"],
            [12, 46, 0, "1kr", "silver coin"],
            [13, 26, 0, "bottle top", "picnic trash"],
            [13, 30, 0, "bottle top", "picnic trash"],
            [13, 46, 0, "bottle top", "picnic trash"],
            [14, 6,  0, "25 ore", "silver coin"],
            [14, 29, 0, "bottle top", "picnic trash"],
            [35, 50, 0, "iron", "iron"],
            [26, 39, 0, "iron", "iron"]
        ]

        # shuffle(self.da)
        # self.do = buildData(self.da, l=l)
        # self.data = self.do.data
        # self.target = self.do.target
        # self.target_data = self.do.target_data

    def rebuild(self, l=4):
        # shuffle(self.da)
        self.do = buildData(self.da, l=l)
        self.data = self.do.data
        self.target = self.do.target
        self.target_data = self.do.target_data
        print(self.target_data)

print("Datasets Loaded")