from __future__ import print_function

import students

import matplotlib.pyplot as plt
import numpy as np
import pickle as pkl
from time import time

from sklearn.grid_search import GridSearchCV
from sklearn.metrics import classification_report
from sklearn.metrics import confusion_matrix
from sklearn.ensemble import RandomForestClassifier


##
## Get and train a random forest classifier
##
def get_trained_classifier(folder, w, h):

	##
	## load data
	##
	images, names = students.load_student_database( folder, w, h )
	X = [ image.flatten() for image in images ]
	y = names
	
	##
	## classifier: Random Forest
	##
	clf = RandomForestClassifier(n_jobs = 1, n_estimators = 100)
	##
	## fit
	##
	clf = clf.fit(X, y)
	return clf

##
## Pickle Dump
##
def pickle_classifier(clf):	

	with open("classifier.pkl", "wb") as keeptrace:
	    pickler = pkl.Pickler(keeptrace)
	    pickler.dump(clf)
	    
if __name__ == "__main__":	
	folder = "./faces/"
	w, h = 30, 50		
	
	print("\nTraining...\n")
	
	clf = get_trained_classifier(folder, w, h)
	print(clf)
	pickle_classifier(clf)
	
	print("\nTraining finished!\n")



