import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier

import datasets

h = .02  # step size in the mesh

class Matrix:
    def __init__(self, l=4, max_features=3):
        print("L=%s" % l)

        self.max_features = max_features
        self.names = ["Decision Tree", "Random Forest"]

        self.COLORS = np.array(['#FF3333',  # red
                                '#0198E1',  # blue
                                '#BF5FFF',  # purple
                                '#FCD116',  # yellow
                                '#FF7216',  # orange
                                '#4DBD33',  # green
                                '#87421F',  # brown
                                '#CC00CC',  # pink
                                '#000000',  # black
                                '#00FF00',  # lime
                                '#0000FF',  # blue pure
                                '#000080',  # navy
                                '#008080',  # teal
                                '#800080',  # purple
                                '#008000',  # green
                                '#808000',  # olive
                                '#800000'
                                ])
        self.classifiers = [
            # KNeighborsClassifier(n_neighbors=3, weights='distance'),
            # SVC(kernel="linear", C=0.025),
            # SVC(gamma=1, C=1),
            # GaussianProcessClassifier(1.0 * RBF(1.0), warm_start=True),
            DecisionTreeClassifier(max_depth=5, max_features=max_features),
            RandomForestClassifier(max_depth=5, n_estimators=10, max_features=max_features),
            # MLPClassifier(alpha=1),
            # AdaBoostClassifier(),
            # GaussianNB()
        ]

        # place to hold the compiled classifiers grouped with their names
        self.compiled_classifiers = zip(self.names, self.classifiers)

        # temp place to hold classifiers while compiling them
        self.tmp_clf = []

        # init the sweden dataset
        self.mydata = datasets.sweden_data(l=l, max_features=max_features)

        # rebuild the database
        self.mydata.rebuild(l=l)

        # rebuild the classifiers
        self.rebuild(l=l)

    def rebuild(self, l=4):
        print("Rebuilding")
        self.mydata.rebuild(l=l)
        # os.system("say 'Rebuilding matrix'")
        self.X = self.mydata.data
        self.y = self.mydata.target
        self.lookup_d = self.mydata.target_data

        self.linearly_separable = (self.X, self.y)

        self.datasets = [self.linearly_separable]
        # iterate over datasets
        for ds_cnt, ds in enumerate(self.datasets):
            # preprocess dataset, split into training and test part
            X, y = ds

            # iterate over classifiers
            for name, clf in zip(self.names, self.classifiers):
                # print(X)
                clf.fit(X, y)
                # os.system("say '%s initialized'" % name)

                self.tmp_clf.append(clf)

                # print(self.mydata.target_data[clf.predict(np.array([11, 46]).reshape(1, -1))[0]])
                # print(self.mydata.target_data[clf.predict(np.array([12, 40]).reshape(1, -1))[0]])
                # print(self.mydata.target_data[clf.predict(np.array([11, 20]).reshape(1, -1))[0]])
                # print(self.mydata.target_data[clf.predict(np.array([33, 48]).reshape(1, -1))[0]])
                #
                # for i in clf.predict(np.array([12, 40, 12, 41, 12, 46]).reshape(3, 2)):
                #     print("est: %s" % self.mydata.target_data[i])

        self.compiled_classifiers = zip(self.names, self.tmp_clf)
        print("AI Initialized")
