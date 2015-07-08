
from multiprocessing import Pool, Process

import itertools


"""
Logistic Regression
"""
from SQN.LogisticRegression import LogisticRegression
from SQN.LogisticRegressionTest import LogisticRegressionTest

from SQN.NewSQN import SQN
from SQN.SGD import SGD

# from SQN.PSQN import PSQN
import numpy as np
import timeit
import data.datasets as datasets
import sys
from SQN import stochastic_tools
import re


def get_batchsizes_from_name(filepath):
        filename = filepath.split("/")[-1]
        filename = filename.split("_")
        b_G = int(filename[0])
        b_H = int(filename[1])
        return b_G, b_H

def load_result_file(filepath):
        
        resfile = open(filepath, "r")
        
        iters, fevals, gevals, adp, f_S, g_norm_S, time = [], [], [], [], [], [], []
        for count, line in enumerate(iter(resfile)):
                line = re.sub('\s', '', str(line))
                entries = re.split(",", str(line))
                
                iters.append( int(entries[0]) )
                fevals.append( int(entries[1]) )
                gevals.append( int(entries[2]) )
                adp.append( int(entries[3]) )
                f_S.append( float(entries[4]) )
                g_norm_S.append( float(entries[5]) )
                time.append( float(entries[6]) )
                
        return iters, fevals, gevals, adp, f_S, g_norm_S, time
                
def load_result_file_w(filepath):
        
        resfile = open(filepath, "r")
        w = []
        for count, line in enumerate(iter(resfile)):
                line = re.sub('\s', '', str(line))
                entries = re.split(",", str(line))
                w.append([float(s) for s in entries])
        return w



def print_f_vals(sqn, options, filepath, testcase=None, rowlim=None):
    
    t_start = timeit.default_timer() #get current system time
    print("\nSQN, Higgs-Dataset\n")
    logreg = LogisticRegression(lam_1=0.0, lam_2=0.0)
    logreg.get_sample = lambda l, X, z: datasets.get_higgs_mysql(l)
    sqn.set_start(dim=sqn.options['dim'])
    w = sqn.get_position()

    sqn.set_options({'sampleFunction': logreg.sample_batch})
    X, z = None, None
    
    if filepath is not None:
        ffile = open(filepath, "w+")
        wfile = open(filepath+"_w.txt", "w+")
    
    sep = ","
    results = []
    locations = []
    f_evals = []
    for k in itertools.count():
        w = sqn.solve_one_step(logreg.F, logreg.G, k=k)
        
        #X_S, z_S = sqn._draw_sample(b = 100)
        #f_evals.append(logreg.F(w, X_S, z_S))
        #print(np.mean(f_evals))
        
        if k%20 == 0 and sqn._is_stationary():
                print sqn._get_test_variance()
                print sqn.options['batch_size'], sqn.options['batch_size_H']
                if sqn.options['batch_size'] <= 1e4 and sqn.options['batch_size_H'] < 4e3:
                    sqn.set_options({'batch_size': sqn.options['batch_size']+1000, 'batch_size_H': sqn.options['batch_size_H']+400})
                
        results.append([k, logreg.fevals, logreg.gevals, logreg.adp, sqn.f_vals[-1], sqn.g_norms[-1], timeit.default_timer()-t_start])
        locations.append(w)
        
        if filepath is not None:
            line = sep.join([ str(r) for r in results[-1] ])[:-1] + "\n"
            ffile.write(line)
            wfile.write(sep.join([str(l) for l in locations[-1]]) + "\n")
        else:    
            print(k, logreg.adp, "%0.2f, %0.2f" % (float(sqn.f_vals[-1]), float(sqn.g_norms[-1])))
        if k > sqn.options['max_iter'] or sqn.termination_counter > 4:
            iterations = k
            break
    if filepath is not None:
        ffile.close()
        wfile.close()
    
    return results
    
def benchmark(batch_size_G, batch_size_H, updates_per_batch, options):
        folderpath = "../outputs/"
        filepath =  folderpath + "%d_%d_%d.txt" %(b_G, b_H, updates_per_batch)
        options['batch_size'] = b_G
        options['batch_size_H'] = b_H
        options['updates_per_batch'] = updates_per_batch
        sqn = SQN(options)
        print_f_vals(sqn, options, filepath)

"""
Main
"""
if __name__ == "__main__":
    
        """
        Runs SQN-LogReg on the Higgs-Dataset,
        which is a 7.4GB csv file for binary classification
        that can be obtained here:
        https://archive.ics.uci.edu/ml/datasets/HIGGS
        the file should be in <Git Project root directory>/datasets/
        """
        options = { 'dim':29, 
                            'N': 5*1e6,
                            'L': 20, 
                            'M': 10, 
                            'beta':5., 
                            'max_iter': 1000, 
                            'batch_size': 100, 
                            'batch_size_H': 0, 
                            'updates_per_batch': 1, 
                            'testinterval': 0
                        }
        
        
        import sys
        if len(sys.argv) > 1:
                print sys.argv
                b_G, b_H = int(sys.argv[1]), int(sys.argv[2])
                updates_per_batch = 1
                benchmark(b_G, b_H, updates_per_batch, options)
        else:
                batch_sizes_G = [100, 1000]#, 10000]        
                batch_sizes_H = [0, 100]#, 1000]
                updates_per_batch = 1
                
                for b_G in batch_sizes_G:
                        for b_H in batch_sizes_H:
                                p = Process(target=benchmark(b_G, b_H, updates_per_batch, options))
                                p.start()
                
    