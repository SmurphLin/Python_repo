import numpy as np
import pandas as pd
from functools import wraps, reduce


test_x = np.array([[1,1,1,1,1],[0,1,2,3,4]])
test_y = np.array([[1],[3],[7],[13],[21]])

theta = np.array([np.zeros(test_x.shape[0])]).transpose()

h = np.dot(theta.transpose(), test_x)
errors = np.subtract(h, test_y.transpose())
updates = np.dot(errors, test_x.transpose()).transpose()
theta =  theta - 0.05*updates




def gradient(features, obs, alpha, iterations):
    """basic gradient descent"""

    theta = np.array([np.zeros(test_x.shape[0])]).transpose()
    cntr = 0
    while cntr < iterations:
        h = np.dot(theta.transpose(), features)
        errors = np.subtract(h, obs.transpose())
        updates = np.dot(errors, features.transpose()).transpose()
        theta = theta - (1/features.shape[1])*alpha*updates
        cntr += 1
    return theta




class GradientDescent(object):
    """gradient descent class"""

    def __init__(self, features, obs):

        self.features = features
        self.obs = obs
        try:
            if isinstance(features, np.ndarray):
                self.theta = np.array([np.zeros(features.shape[0])]).transpose()
            else:
                raise TypeError('features is not a numpy array \n')
        except TypeError as te:
            print(te)

        self.sim_results = []
        self.cleaned_results = []
        self.cntr = 0
        self.iterations = [10, 20, 50, 100, 200, 1000]
        self.alpha = [0.001, 0.01, 0.05, 0.10, 0.25, 1]


    def simulate_descent(self):
        """run a gradient descent test simulation"""
        theta_list = []
        for a in self.alpha:
            alpha_list = []
            a_temp = []
            for i in self.iterations:
                # reset the theta value
                this_theta = self.theta
                iteration_list = []
                temp = []
                for j in range(i):
                    h = np.dot(this_theta.transpose(), self.features)
                    errors = np.subtract(h, self.obs.transpose())
                    updates = np.dot(errors, self.features.transpose()).transpose()
                    this_theta = (this_theta - a * updates)
                    theta_list.append(this_theta.flatten())
                    temp.append(j)
                iteration_list.append([i, temp, theta_list])
                a_temp.append(a)
            alpha_list.append([a_temp, iteration_list, theta_list])
            self.sim_results.append(alpha_list)

















g = GradientDescent(features=test_x, obs=test_y)
g.simulate_descent()
g.sim_results
print(np.array(g.sim_results).flatten())