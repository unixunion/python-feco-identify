import numpy as np
import os
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
    def __init__(self, aray, l=4, max_features=2):

        # create data, target and target_data lists
        self.data = []
        self.target = []
        self.target_data = []
        self.target_names = [] # names of individual finds

        if max_features == 2:
            print("2 feature mode")
        elif max_features == 3:
            print("3 feature mode")

        # iterate over the objects in the array, appending co-ordintates and labeling
        for i in aray:

            if max_features==2:
                self.data.append([i[0], i[1]])
            elif max_features==3:
                self.data.append([i[0], i[1], i[2]])

            # check if the "label" value is already present in the target_data list
            if not i[l] in self.target_data:
                self.target_data.append(i[l])
            self.target.append(self.target_data.index(i[l]))
            self.target_names.append(i[3])

        self.data = np.array(self.data)


# mixed bag of "common" finds using 2 coordinates only
# this should be improved to use 3x 2 coordinates scanned at 3 different angles.
# fe co
class sweden_data:
    def __init__(self, l=4, max_features=3):
        # source data fe, co, depth, name, category
        self.da = [
            [2, 42,  10, "5kr", "silver coin"],
            [3, 46,  10, "2kr", "silver coin"],
            [5, 47,  10, "2kr", "silver coin"],
            [6, 46,  10, "2kr", "silver coin"],
            [9, 26,  10, "5kr", "silver coin"],
            [9, 38,  10, "50 ore", "silver coin"],
            [10, 28, 5, "wine top", "picnic trash"],
            [11, 4,  10, "10 ore", "silver coin"],
            [11, 20, 5, "pull tab", "picnic trash"],
            [11, 22, 5, "pull tab", "picnic trash"],
            [11, 25, 2, "5kr", "CuNi coin"],
            [11, 46, 12, "2/3 skillning", "copper coin"],
            [11, 46, 12, "1kr", "silver coin"],
            [12, 6,  15, "25 ore", "bronze coin"],
            [12, 17, 2, "1kr", "CuNi coin"],
            [12, 18, 5, "pull tab", "picnic trash"],
            [12, 21, 5, "pull tab", "picnic trash"],
            [12, 22, 4, "pull tab", "picnic trash"],
            [12, 22, 2, "bottle top", "picnic trash"],
            [12, 24, 5, "bottle top", "picnic trash"],
            [12, 24, 1, "pull tab", "picnic trash"],
            [12, 25, 5, "bottle top", "picnic trash"],
            [12, 26, 8, "10 ore", "silver coin"],
            [12, 28, 3, "bottle top", "picnic trash"],
            [12, 28, 8, "1 ore", "copper coin"],
            [12, 28, 5, "wine top", "picnic trash"],
            [12, 31, 4, "wine top", "picnic trash"],
            [12, 32, 10, "25 ore", "silver coin"],
            [12, 34, 12, "2 ore", "copper coin"],
            [12, 38, 11, "2 ore", "copper coin"],
            [12, 39, 5, "bottle top", "picnic trash"],
            [12, 40, 11, "5 ore", "bronze coin"],
            [12, 40, 10, "5 ore", "bronze coin"],
            [12, 40, 3, "10kr", "nordic gold coin"],
            [12, 41, 6, "5 ore", "copper coin"],
            [12, 42, 2, "1kr", "CuNi copper Coin"],
            [12, 42, 7, "5 ore", "bronze coin"],
            [12, 42, 5, "bottle top", "picnic trash"],
            [12, 44, 10, "25 ore", "silver coin"],
            [12, 45, 10, "50 ore", "silver coin"],
            [12, 46, 14, "1kr", "silver coin"],
            [13, 26, 5, "bottle top", "picnic trash"],
            [13, 30, 6, "bottle top", "picnic trash"],
            [13, 46, 4, "bottle top", "picnic trash"],
            [14, 6,  12, "25 ore", "silver coin"],
            [14, 29, 5, "bottle top", "picnic trash"],
            [35, 50, 12, "iron", "iron"]
        ]

        self.max_features=max_features
        print("%s feature mode" % max_features)

    def rebuild(self, l=4):
        # shuffle(self.da)
        print("Rebuilding with %s features" % self.max_features)
        self.do = buildData(self.da, l=l, max_features=self.max_features)
        self.data = self.do.data
        self.target = self.do.target
        self.target_data = self.do.target_data
        self.target_names = self.do.target_names
        print(self.target_data)

print("Datasets Loaded")