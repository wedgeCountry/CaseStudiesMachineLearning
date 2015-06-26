# -*- coding: utf-8 -*-
"""
Created on Wed Jun 24 22:48:16 2015

@author: Fin Bauer
"""

import numpy as np

def proximal_gradient(f, grad_f, x0, t, **options):
    """
    proximal gradient for l1 regularization
    """
    
    options.setdefault('l', 1)
    
    x_old = x0
    
    for i in range(300):
        
        x_new = prox(x_old - t * grad_f(x_old), t, **options)
        s = x_new - x_old
        
        if np.linalg.norm(s) < 1e-8:
            break
        
        x_old = x_new
        
        print(f(x_new))
    
    return x_new
    
def prox(x, t, **options):
    
    return np.maximum(x - t * options['l'], 0) - np.maximum(-x - t * 
                        options['l'], 0)


if __name__ == "__main__":
    from scipy.linalg import eigvals
    from time import time
    A = np.random.normal(size = (1500, 3000))
    b = np.random.normal(size = (1500, 1))
    A_sq = np.dot(A.T, A)
    Ab = np.dot(A.T, b)

    def z(x):
    
        temp = np.dot(A, x) - b
    
        return 1 / 2 * np.dot(temp.T, temp)
    
    def grad_z(x):
        
        return  np.dot(A_sq, x) - Ab
        
    x0 = np.ones((3000,1))
    L = eigvals(A_sq).real.max()
    
    t0 = time()
    x = proximal_gradient(z, grad_z, x0, 1 / L, l = 10)
    print(time() - t0)