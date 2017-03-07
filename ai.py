import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier

import datasets

h = .02  # step size in the mesh

names = ["Decision Tree", "Random Forest"]

COLORS = np.array(['#FF3333',  # red
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
                   ])

classifiers = [
    # KNeighborsClassifier(n_neighbors=3, weights='distance'),
    # SVC(kernel="linear", C=0.025),
    # SVC(gamma=1, C=1),
    # GaussianProcessClassifier(1.0 * RBF(1.0), warm_start=True),
    DecisionTreeClassifier(max_depth=5),
    RandomForestClassifier(max_depth=5, n_estimators=10, max_features=2),
    # MLPClassifier(alpha=1),
    # AdaBoostClassifier(),
    # GaussianNB()
]

compiled_classifiers = []

mydata = datasets.sweden_data(l=3)

X = mydata.data
y = mydata.target
lookup_d = mydata.target_data

linearly_separable = (X, y)

datasets = [linearly_separable]

i = 1
# iterate over datasets
for ds_cnt, ds in enumerate(datasets):
    # preprocess dataset, split into training and test part
    X, y = ds
    X_train, X_test, y_train, y_test = \
        train_test_split(X, y, test_size=0.4)  # , random_state=42

    x_min, x_max = X[:, 0].min() - 1, X[:, 0].max() + 1
    y_min, y_max = X[:, 1].min() - 1, X[:, 1].max() + 1
    xx, yy = np.meshgrid(np.arange(x_min, x_max, h),
                         np.arange(y_min, y_max, h))

    i += 1

    # iterate over classifiers
    for name, clf in zip(names, classifiers):
        clf.fit(X, y)

        compiled_classifiers.append(clf)

        print(mydata.target_data[clf.predict(np.array([11,46]).reshape(1, -1))[0]])
        print(mydata.target_data[clf.predict(np.array([12,40]).reshape(1, -1))[0]])
        print(mydata.target_data[clf.predict(np.array([11,20]).reshape(1, -1))[0]])
        print(mydata.target_data[clf.predict(np.array([33,48]).reshape(1, -1))[0]])
