import datasets
from sklearn import svm, metrics
import numpy as np

etrac = datasets.sweden_data()

data_and_labels = list(zip(etrac.data, etrac.target))

n_samples = len(etrac.data)
data = etrac.data.reshape((n_samples, -1))

# Create a classifier: a support vector classifier
classifier = svm.SVC(probability=True, gamma=0.5, C=1000)
classifier.fit(data[:n_samples], etrac.target[:n_samples])

# Now predict the value of the digit on the second half:
expected = etrac.target[n_samples / 2:]
predicted = classifier.predict(data[n_samples / 2:])

print(etrac.target_data[classifier.predict(np.array([12,40]).reshape(1, -1))[0]])
print(etrac.target_data[classifier.predict(np.array([11,21]).reshape(1, -1))[0]])


print("Classification report for classifier %s:\n%s\n"
      % (classifier, metrics.classification_report(expected, predicted)))
print("Confusion matrix:\n%s" % metrics.confusion_matrix(expected, predicted))
