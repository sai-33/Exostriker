 #!/usr/bin/python


__author__ = 'Trifon Trifonov'

import sys, os
#sys.path.insert(0, '../lib')
import numpy as np
import jac2astrocen
import corner

import re
from subprocess import PIPE, Popen 
import signal 
import tempfile, shutil
from threading import Thread
from Warning_log import Warning_log
import scipy.stats as pdf
import dill
from scipy.signal import argrelextrema
from scipy.ndimage import gaussian_filter


TAU= 2.0*np.pi 


 
def transit_tperi(per, ecc, om, ma, epoch):
    '''
    '''
    om = np.radians(om)
    ma = np.radians(ma)

    E = 2.0*np.arctan( np.sqrt( ( (1.0-ecc)/(1.0+ecc) ) ) * np.tan( (np.pi/4.0)-(om/2.0) ) )
   # print(E)
    t_peri    = epoch  - ((ma/TAU)*per)
    t_transit = t_peri + (E + ecc*np.sin(E)) * (per/TAU)    

    return t_peri, t_transit    

    
def ma_from_t0(per, ecc, om, t_transit, epoch):
    '''
    '''
    om = np.radians(om)
    E = 2.0*np.arctan( np.sqrt( ( (1.0-ecc)/(1.0+ecc) ) ) * np.tan( (np.pi/4.0)-(om/2.0) ) )
 
   # t_transit = epoch  - ((ma/TAU)*per) + (E + ecc*np.sin(E)) * (per/TAU)          
    
    ma =  ((epoch  - t_transit + (E + ecc*np.sin(E)) * (per/TAU))*TAU)/per 
    ma = np.degrees(ma)%360.0

    return ma   





def get_mode_of_samples(samples, nsamp): 

    mode_samp = []
   # err1_samp = []
  #  err2_samp = []
 
    
    for i in range(nsamp):
    	#ci = np.percentile(samples[:,i], [level, 100.0-level])
    	#mmm = stats.binned_statistic(np.array([samples[:,i]]), axis=None)
        n, b = np.histogram(samples[:,i], bins=100)
        n = gaussian_filter(n, 1.0)
        x0 = np.array(list(zip(b[:-1], b[1:]))).flatten()
        y0 = np.array(list(zip(n, n))).flatten()	
        k  = np.unravel_index(y0.argmax(),y0.shape)
        mode_samp.append(x0[k])
        #err1_samp.append(x0[k]- ci[0])
        #err2_samp.append(ci[1]- x0[k])        
   # print el_str[i],'=', x0[k], "- %s"%(x0[k]-ci[0]), "+ %s"%(ci[1]  - x0[k] )
    return mode_samp #,err1_samp,err2_samp

def get_mean_of_samples(samples, nsamp): 

    mean_samp = []
    
    for i in range(nsamp):
        mean_samp.append(np.mean(samples[:,i]))
    return mean_samp #,err1_samp,err2_samp

def get_best_lnl_of_samples(samples,lnl, nsamp): 

    best_ln_samp = []
    lnL_best_idx = np.argmax(lnl)
    lnL_best = lnl[lnL_best_idx]    
 
    
    for i in range(nsamp):    
 
        minlnL = samples[lnL_best_idx,i] 
        best_ln_samp.append(minlnL)
        
    
    return best_ln_samp,lnL_best #,err1_samp,err2_samp





def cornerplot(obj, fileinput=False, level=(100.0-68.3)/2.0,type_plot = 'mcmc', **kwargs): 

    #obj = dill.copy(copied_obj)
    '''Generates a corner plot visualizing the mcmc samples. Optionally samples can be read from a file.'''
    #self.mcmc_sample_file = 'mcmc_samples'+'_%s'%mod
    #self.corner_plot_file = 'cornerplot.png'
    if(fileinput):
        if type_plot == 'mcmc':
            samples=read_file_as_array_of_arrays_mcmc(obj.mcmc_sample_file)
        if type_plot == 'nest':
            samples=read_file_as_array_of_arrays_mcmc(obj.nest_sample_file)        
   # elif(obj.sampler_saved):
   #     samples=obj.sampler.samples
    else:
        raise Exception ('Please run mcmc/nested sampling and save sampler or provide a valid samples file!')
    #print(len(obj.e_for_mcmc),len(samples),obj.e_for_mcmc)
    fig = corner.corner(samples,bins=25, color="k", reverse=True, upper= True, labels=obj.e_for_mcmc, quantiles=[level/100.0, 1.0-level/100.0], 
                        levels=(0.6827, 0.9545,0.9973), smooth=1.0, smooth1d=1.0, plot_contours= True, show_titles=True, truths=obj.par_for_mcmc, 
                        dpi = 300, pad=15, labelpad = 50 ,truth_color ='r', title_kwargs={"fontsize": 12}, scale_hist=True,  no_fill_contours=True, 
                        plot_datapoints=True, kwargs=kwargs)
    
    if type_plot == 'mcmc':
        fig.savefig(obj.mcmc_corner_plot_file)  
    if type_plot == 'nest':
        fig.savefig(obj.nest_corner_plot_file)  
 
    return          
       


def planet_orbit_xyz(obj, planet):

    u1 = obj.params.stellar_mass * (4*np.pi*np.pi)/(365.25*365.25)
    mean_orb = np.linspace(0,2.0*np.pi, 360.0)
    
    x = np.zeros(len(mean_orb))
    y = np.zeros(len(mean_orb))
    z = np.zeros(len(mean_orb))
    u = np.zeros(len(mean_orb))
    v = np.zeros(len(mean_orb))
    w = np.zeros(len(mean_orb))
    
    dist =  np.zeros(len(mean_orb))
        
    q = (1.0 - obj.params.planet_params[2 + int(planet)*7])*float(obj.fit_results.a[int(planet)])
    
    
    #this need to be fixed to work with arrays
    for f in range(len(mean_orb)):
        x[f],y[f],z[f],u[f],v[f],w[f] = jac2astrocen.mco_el2x(u1,q,
                                                       obj.params.planet_params[2 + int(planet)*7],
                                                       np.radians(obj.params.planet_params[5 + int(planet)*7]-90.0),
                                                       np.radians(obj.params.planet_params[3 + int(planet)*7]) - np.radians(obj.params.planet_params[6 + int(planet)*7]),
                                                       np.radians(obj.params.planet_params[6 + int(planet)*7] ), mean_orb[f])    
                                                       
        dist[f] =  np.sqrt(x[f]**2.0 + y[f]**2.0 + z[f]**2.0)                                        
    
    x_p,y_p,z_p,u_p,v_p,w_p = jac2astrocen.mco_el2x(u1,q,
                                                       obj.params.planet_params[2 + int(planet)*7],
                                                       np.radians(obj.params.planet_params[5 + int(planet)*7] -90.0),
                                                       np.radians(obj.params.planet_params[3 + int(planet)*7]) - np.radians(obj.params.planet_params[6 + int(planet)*7]),
                                                       np.radians(obj.params.planet_params[6 + int(planet)*7]), np.radians(obj.params.planet_params[4 + int(planet)*7]))    
 

    min_index = np.unravel_index(np.argmin(dist, axis=None), dist.shape)                                                    
    max_index = np.unravel_index(np.argmax(dist, axis=None), dist.shape)                                                                                                           
                                                       
    return np.array([x,y,z,u,v,w]), np.array([x_p,y_p,z_p,u_p,v_p,w_p]), np.array([x[min_index],y[min_index],z[min_index],u[min_index],v[min_index],w[min_index]]), np.array([x[max_index],y[max_index],z[max_index],u[max_index],v[max_index],w[max_index]])

   
 

def create_temporary_copy(path): # not really a good idea......
    '''
    creates a temp_ velocity file in the root directory of the GUI.   
    
    input: full path to the file  
    output: temp_name of the file to be loaded
    '''    

    dirname, basename = os.path.split(path)
    temp_dir = './'#tempfile.gettempdir()
    temp_path = os.path.join(temp_dir, '.temp_'+basename)
    shutil.copy2(path, temp_path)
    #temp = tempfile.NamedTemporaryFile(prefix=basename, dir='./',delete=False)
    return temp_path

def copy_file_to_datafiles(path):
    '''
    creates a temp_ velocity file in the root directory of the GUI.   
    
    input: full path to the file  
    output: temp_name of the file to be loaded
    '''    

    dirname, basename = os.path.split(path)
    temp_dir = './datafiles'#tempfile.gettempdir()   
    temp_path = os.path.join(temp_dir, basename)
    
    os.system("cp %s %s"%(path, temp_path))
    #print(temp_path, path)
   # if os.path.exists(temp_path):
    #    try:
   #         shutil.copy2(path, temp_path)
   #     except shutil.Error:
   #         temp_path == path    
 
        #os.system("cp %s %s"%(path, temp_path))
    #temp = tempfile.NamedTemporaryFile(prefix=basename, dir='./',delete=False)
    return temp_path

def mut_incl(i1,i2,capOm):
    '''
    Calculates the mutual inclination of two planets   
    
    input parameters:
    
    i1,i2, Delta Omega: inclinations and diffence of the line of nodes in deg.
  
    output parameters:    
     
    Delta i: mutual orbital inclination in deg.
    '''
    fb = np.degrees(np.arccos(((np.cos(np.radians(i1))*np.cos(np.radians(i2)))+
    (np.sin(np.radians(i1))*np.sin(np.radians(i2))*np.cos(np.radians(capOm))))))
    return fb
 
def add_jitter(obj, errors, ind):
    
    errors_with_jitt = np.array([np.sqrt(errors[i]**2 + obj.params.jitters[ii]**2)  for i,ii in enumerate(ind)])
    return errors_with_jitt 
    

def get_RV_data(obj, file, idset_ts, jitter=False, o_c=False, print_data=False, width = 10, precision = 3):
 
    if len(obj.filelist.idset)==0:
        return
    
   # if idset_ts ==0:
   #     print("dataset IDs start from 1")
   #     return
   # elif len(np.atleast_1d(idset_ts)) > 1:
   #     if 0 in idset_ts:
   #         print("dataset IDs start from 1")
   #         return            
            
    #if not os.path.exists(path):
   #     os.makedirs(path)
 
    output_file = str(file) 
    f = open(output_file, 'w') 
    
    idset_ts = np.array(np.atleast_1d(idset_ts)) #-1
    
    
    JD = obj.fit_results.rv_model.jd
    if not o_c:
        rv = obj.fit_results.rv_model.rvs
    else:
        rv = obj.fit_results.rv_model.o_c    
    id_set = obj.filelist.idset
    
    if jitter==True:
        sigma = add_jitter(obj,obj.fit_results.rv_model.rv_err, id_set)   
    else:
        sigma =  obj.fit_results.rv_model.rv_err 
 
    
    if len(idset_ts)==1:
      
        for i in range(len(JD[id_set==idset_ts[0]])):  
            if print_data  ==  True:
                print(float(JD[i]), float(rv[i]), float(sigma[i]))
        f.write('{0:{width}.{precision}f}  {1:{width}.{precision}f}  {2:{width}.{precision}f}  \n'.format(float(JD[i]), float(rv[i]), float(sigma[i]),  width = width, precision = precision )   ) 
    else:
        
        for i in range(len(idset_ts)):
            for ii in range(len(JD)):   
                 if int(id_set[ii]) != int(idset_ts[i]):
                     continue
                 else:
	                 f.write('{0:{width}.{precision}f}  {1:{width}.{precision}f}  {2:{width}.{precision}f}  {3:{width}.{precision}f}  \n'.format(float(JD[ii]), float(rv[ii]), float(sigma[ii]), idset_ts[i], width = width, precision = precision )   )          
    
    f.close()   
    print('Done!')    
    return 
  
def get_RV_model(obj, file, width = 10, precision = 4):
 
    if len(obj.fit_results.rv_model.jd)==0:
        return
    
    #if not os.path.exists(path):
   #     os.makedirs(path)
 
    output_file = str(file) 
    f = open(output_file, 'w') 
    
    
    JD = obj.fit_results.model_jd
    
    if obj.doGP == True:
        y_model = obj.fit_results.model + obj.gp_model_curve[0]
    else:
        y_model = obj.fit_results.model     
        
    for i in range(len(JD)):  
       # f.write('%.4f   %.4f  \n'%(float(JD[i]), float(y_model[i]) ))  
        f.write('{0:{width}.{precision}f}  {1:{width}.{precision}f} \n'.format(float(JD[i]), float(y_model[i]), width = width, precision = precision) )
    f.close()   
    print('Done!')
    return 



def run_command_with_timeout(args, secs, output=False, pipe=False): # set output=True if you need to save the output
    '''
    Run a command and kill if it takes too long.
    '''


   # print(args)
    if not (pipe):
        text=tempfile.TemporaryFile() # because PIPE usually has too low capacity
        proc = Popen(args, shell=True, preexec_fn=os.setsid, stdout=text, stderr=text)
    else:
        proc = Popen(args, shell=True, preexec_fn=os.setsid, stdout=PIPE, stderr=PIPE)  
   # print(proc)    
    proc_thread = Thread(target=proc.wait)
    proc_thread.start()
    proc_thread.join(secs)
    if proc_thread.is_alive():
        #print (proc.pid)
        try:
            os.killpg(proc.pid, signal.SIGTERM)
        except OSError:
            pass
        print('Process #{} killed after {} seconds'.format(proc.pid, secs))
        flag = -1
        return '',flag
    if not (pipe):
        text.seek(0)
        string_to_output=text.readlines()
    else:
        text=proc.communicate()[0]
        string_to_output=text.splitlines()
    for i in range(len(string_to_output)):
        string_to_output[i]=string_to_output[i].decode('utf-8').split()
    if not (pipe):
        text.close()    
    flag = 1
    if (output):
        return string_to_output,flag # besides the flag which informs about successful termination we also return all the console output in case we want to save it in a variable
    else:
        return '',flag
         
def is_float(n):
    '''
    Given a string n, verify if it expresses a valid float.
    Casting n to string in case an object of type float or similar is given as an argument
    '''
    return re.match(r'^-?\d*(\.\d+)?(E-?\d+)?$', str(n))   

# Given a float or string, verify if it expresses an integer. Possible to introduce upper and lower bounds and if the inequalities on either side should be strong or weak . 
def is_int(s,bounded=[False,False],bounds=[0,0],equal=[False,False]):
    if is_float(s): # if it is an int, it is certainly float as well 
        n=float(s) # we need n as a number, not as a string, for comparisons with bounds later
        is_an_int=float(s).is_integer()
    else:
        is_an_int=False
    # is_an_int now contains an information if s is an int, but without bounds. Let's introduce bounds:
    if(is_an_int): # if it's not an int at all we don't need to check any further
        if(bounded[0]): # if there is a lower bound let's apply it
            if (n<bounds[0] or (not equal[0] and n==bounds[0])):
                is_an_int=False
    if(is_an_int): # if the lower bound returned False we don't need to check any further
        if(bounded[1]): # if there is a lower bound let's apply it
            if (n>bounds[1] or (not equal[1] and n==bounds[1])):
                is_an_int=False
    return is_an_int

# If save_wrong_lines is enabled we will save a string 'wrong_line' instead of this line and save indices at which this occurred, otherwise we will skip this line
def convert_array_to_float(a,save_wrong_lines=False): 
    converting_warnings=Warning_log([],'Converting array to float')
    b=[]
    if (save_wrong_lines):
        wrong_indices=[]
    for i in range(len(a)):
        if not is_float(a[i]):
            if not (save_wrong_lines):
                converting_warnings.update_warning_list('Array passed to convert_array_to_float function should only contain floats! Line %d skipped'%(i+1))
            else:
                b.append('wrong_line')
                wrong_indices=np.concatenate((wrong_indices,np.atleast_1d(i)))
        else:
            b.append(float(a[i]))
            
    converting_warnings.print_warning_log()
    if (save_wrong_lines):
        return np.array(b),wrong_indices  
    else:
        return np.array(b)

def convert_array_to_int(a, save_wrong_lines=False):
    converting_warnings=Warning_log([],'Converting array to int')
    b=[]
    if (save_wrong_lines):
        wrong_indices=[]
    for i in range(len(a)):
        if not is_int(a[i]):
            if not (save_wrong_lines):
                converting_warnings.update_warning_list('Array passed to convert_array_to_int function should only contain ints! Line %d skipped'%(i+1))
            else:
                b.append('wrong_line')
                wrong_indices=np.concatenate((wrong_indices,np.atleast_1d(i)))
        else:
            b.append(int(a[i]))
            
    converting_warnings.print_warning_log()
    if (save_wrong_lines):
        return np.array(b),wrong_indices  
    else:
        return np.array(b)

#for convenient reading of the input file    
def read_file_as_array_of_arrays(inputfile): 
    a=open(inputfile, 'r')
    b=a.readlines() # b as array of strings
    c=[]
    ic=0 # iterator for values in c
    for i in range(len(b)): 
        b[i]=np.atleast_1d(b[i].split()) # turn a row of b into an array of arrays
        c.append([]) # need to make a separate array so every element is of correct type
        # convert each string that represents a float into float
        for j in range(0,len(b[i])): 
            if (is_float(b[i][j])):
                c[ic].append(float(b[i][j]))
            elif not (b[i][j][-1]==':'): # ignore comments, which can be place by the user as strings which end with a collon, in the comments use underline instead of space or an error will arise
                c[ic].append(b[i][j])
        ic=ic+1
    #c = np.array(c, dtype=float)    
        
    return c


#for convenient reading of the input file  the second is a hack so the mcmc lnL line is skipped! TBFixed  
def read_file_as_array_of_arrays_mcmc(inputfile): 
    a=open(inputfile, 'r')
    b=a.readlines() # b as array of strings
    c=[]
    ic=0 # iterator for values in c
    for i in range(len(b)): 
        b[i]=np.atleast_1d(b[i].split()) # turn a row of b into an array of arrays
        c.append([]) # need to make a separate array so every element is of correct type
        # convert each string that represents a float into float
        for j in range(1,len(b[i])): 
            if (is_float(b[i][j])):
                c[ic].append(float(b[i][j]))
            elif not (b[i][j][-1]==':'): # ignore comments, which can be place by the user as strings which end with a collon, in the comments use underline instead of space or an error will arise
                c[ic].append(float(b[i][j]))
        ic=ic+1
    
    c = np.array(c, dtype=float)    
    return c


    
def verify_array_with_bounds(ar,bounds):
    '''Verify if values of array ar fit withind declared bounds, if too many/too few bounds do as much as can be done'''
    if (len(ar)<=len(bounds)):
        num=len(ar) # number of values to check
    elif (len(ar)>len(bounds)):
        num=len(bounds) # number of values to check  
    verification=True # initial value
    for i in range(num):
        # check if some of the values doesn't fit in the bounds, if so return False
        if (ar[i]<bounds[i][0] or ar[i]>bounds[i][1]):
            verification=False
            break       
        
    return verification



    
def latex_pl_param_table(obj, width = 10, precision = 2, asymmetric = False, file_name='test.tex',path='./'):
    

    if asymmetric != True:
        
        text = '''       
    \\begin{table}[ht]
    % \\begin{adjustwidth}{-4.0cm}{} 
    % \\resizebox{0.69\textheight}{!}
    % {\\begin{minipage}{1.1\textwidth}
    
    \centering   
    \caption{{}}   
    \label{table:}      
    
    \\begin{tabular}{lrrrrrrrr}     % 2 columns 
    
    \hline\hline  \\noalign{\\vskip 0.7mm}      
    '''
    
     
        text = text + '''Parameter \hspace{0.0 mm}'''
        for i in range(obj.npl):     
            text = text + '''& Planet %s '''%chr(98+i)
        text = text + '''\\\\
    \hline \\noalign{\\vskip 0.7mm} 
        
        '''
    
        text = text + '''{0:{width}s}'''.format("$K$  [m\,s$^{-1}$]", width = 30)
        for i in range(obj.npl):     
            text = text + '''& {0:{width}.{precision}f} $\pm$ {1:{width}.{precision}f} '''.format(obj.params.planet_params[7*i], max(np.abs(obj.param_errors.planet_params_errors[7*i])), width = width, precision = precision)
        text = text + '''\\\\
        '''        
        text = text + '''{0:{width}s}'''.format("$P$  [day]", width = 30)
        for i in range(obj.npl):     
            text = text + '''& {0:{width}.{precision}f} $\pm$ {1:{width}.{precision}f} '''.format(obj.params.planet_params[7*i +1], max(np.abs(obj.param_errors.planet_params_errors[7*i +1])), width = width, precision = precision)
        text = text + '''\\\\
        '''  
        text = text + '''{0:{width}s}'''.format("$e$  ", width = 30)
        for i in range(obj.npl):     
            text = text + '''& {0:{width}.{precision}f} $\pm$ {1:{width}.{precision}f} '''.format(obj.params.planet_params[7*i +2], max(np.abs(obj.param_errors.planet_params_errors[7*i +2])), width = width, precision = precision)
        text = text + '''\\\\
        '''  
        text = text + '''{0:{width}s}'''.format("$\omega$  [deg]", width = 30)
        for i in range(obj.npl):     
            text = text + '''& {0:{width}.{precision}f} $\pm$ {1:{width}.{precision}f} '''.format(obj.params.planet_params[7*i +3], max(np.abs(obj.param_errors.planet_params_errors[7*i +3])), width = width, precision = precision)
        text = text + '''\\\\
        '''  
        text = text + '''{0:{width}s}'''.format("$M_{\\rm 0}$  [deg]", width = 30)
        for i in range(obj.npl):     
            text = text + '''& {0:{width}.{precision}f} $\pm$ {1:{width}.{precision}f} '''.format(obj.params.planet_params[7*i +4], max(np.abs(obj.param_errors.planet_params_errors[7*i +4])), width = width, precision = precision)
        text = text + '''\\\\
        '''          
        text = text + '''{0:{width}s}'''.format("$i$  [deg]", width = 30)
        for i in range(obj.npl):     
            text = text + '''& {0:{width}.{precision}f} $\pm$ {1:{width}.{precision}f} '''.format(obj.params.planet_params[7*i +5], max(np.abs(obj.param_errors.planet_params_errors[7*i +5])), width = width, precision = precision)
        text = text + '''\\\\    
        '''      
        text = text + '''{0:{width}s}'''.format("$\Omega$  [deg]", width = 30)
        for i in range(obj.npl):     
            text = text + '''& {0:{width}.{precision}f} $\pm$ {1:{width}.{precision}f} '''.format(obj.params.planet_params[7*i +6], max(np.abs(obj.param_errors.planet_params_errors[7*i +6])), width = width, precision = precision)
        text = text + '''\\\\
        '''            
        text = text + '''{0:{width}s}'''.format("$t_{\\rm 0}$  [day]", width = 30)
        for i in range(obj.npl):     
            text = text + '''& {0:{width}.{precision}f} $\pm$ {1:{width}.{precision}f} '''.format(obj.t0[i], max(abs(obj.t0_err[i])), width = width, precision = precision)
        text = text + '''\\\\
        '''            
        text = text + '''{0:{width}s}'''.format("Rad.  [$R_\oplus$]", width = 30)
        for i in range(obj.npl):     
            text = text + '''& {0:{width}.{precision}f} $\pm$ {1:{width}.{precision}f} '''.format(obj.pl_rad[i], max(abs(obj.pl_rad_err[i])), width = width, precision = precision)
        text = text + '''\\\\
        '''            
        text = text + '''{0:{width}s}'''.format("$a$  [$R_\odot$]", width = 30)
        for i in range(obj.npl):     
            text = text + '''& {0:{width}.{precision}f} $\pm$ {1:{width}.{precision}f} '''.format(obj.pl_a[i], max(abs(obj.pl_a_err[i])), width = width, precision = precision)
        text = text + '''\\\\
        '''   
        text = text + '''{0:{width}s}'''.format("$a$  [au]", width = 30)
        for i in range(obj.npl):     
            text = text + '''& {0:{width}.{precision}f} $\pm$ {1:{width}.{precision}f} '''.format(obj.fit_results.a[i], 0, width = width, precision = precision)
        text = text + '''\\\\
        '''      
        text = text + '''{0:{width}s}'''.format("$m \sin i$  [$M_{\\rm jup}$]", width = 30)
        for i in range(obj.npl):     
            text = text + '''& {0:{width}.{precision}f} $\pm$ {1:{width}.{precision}f} '''.format(obj.fit_results.mass[i], 0, width = width, precision = precision)
        text = text + '''\\\\
        '''          
        text = text + '''{0:{width}s}'''.format("$t_{\omega}$  [day]", width = 30)
        for i in range(obj.npl):     
            text = text + '''& {0:{width}.{precision}f} $\pm$ {1:{width}.{precision}f} '''.format((float(obj.epoch) - (np.radians(obj.params.planet_params[7*i + 4])/(2*np.pi))*obj.params.planet_params[7*i + 1] ), 0, width = width, precision = precision)
        text = text + '''\\\\ 
        '''          
     
             
        for i in range(obj.filelist.ndset):   
            text = text + '''{0:{width}s}'''.format("RV$_{\\rm off}$ %s"%(i+1), width = 30)            
            text = text + '''& {0:{width}.{precision}f} $\pm$ {1:{width}.{precision}f} '''.format(float(obj.params.offsets[i]), float(max(np.abs(obj.param_errors.offset_errors[i]))), width = width, precision = precision)
            text = text + '''\\\\
        '''   
        for i in range(obj.filelist.ndset):   
            text = text + '''{0:{width}s}'''.format("RV$_{\\rm jit}$ %s"%(i+1), width = 30)            
            text = text + '''& {0:{width}.{precision}f} $\pm$ {1:{width}.{precision}f} '''.format(float(obj.params.jitters[i]), float(max(np.abs(obj.param_errors.jitter_errors[i]))), width = width, precision = precision)
            text = text + '''\\\\
        '''   
    
        text = text + '''{0:{width}s}'''.format("$\chi^2$", width = 30)            
        text = text + '''& {0:{width}.{precision}f} '''.format(float(obj.fit_results.chi2), width = width, precision = precision)
        text = text + '''\\\\
        '''    
        text = text + '''{0:{width}s}'''.format("$\chi_{\\nu}^2$", width = 30)            
        text = text + '''& {0:{width}.{precision}f} '''.format(float(obj.fit_results.reduced_chi2), width = width, precision = precision)
        text = text + '''\\\\
        '''        
        text = text + '''{0:{width}s}'''.format("$r.m.s.$ [m\,s$^{-1}$]", width = 30)            
        text = text + '''& {0:{width}.{precision}f} '''.format(float(obj.fit_results.rms), width = width, precision = precision)
        text = text + '''\\\\
        '''            
    
        text = text + '''{0:{width}s}'''.format("$-\ln\mathcal{L}$", width = 30)            
        text = text + '''& {0:{width}.{precision}f} '''.format(float(obj.fit_results.loglik), width = width, precision = precision)
        text = text + '''\\\\
        '''        
        text = text + '''{0:{width}s}'''.format("N$_{\\rm RV}$ data", width = 30)            
        text = text + '''& {0:{width}.{precision}f} '''.format(len(obj.fit_results.jd), width = width, precision = 0)
        text = text + '''\\\\
        '''         
        
        text = text + '''{0:{width}s}'''.format("Epoch", width = 30)            
        text = text + '''& {0:{width}.{precision}f} '''.format(obj.epoch, width = width, precision = precision)
        text = text + '''\\\\
        '''           
        
        text = text + '''\\\\
    \hline \\noalign{\\vskip 0.7mm} 
        
        '''     
        
        text = text + '''        
    \end{tabular}  
    
    % \end{minipage}}
    % \end{adjustwidth}
    
    %\\tablefoot{\small }
    
    \end{table}
    '''  

    elif asymmetric == True:

        text = '''       
    \\begin{table}[ht]
    % \\begin{adjustwidth}{-4.0cm}{} 
    % \\resizebox{0.69\textheight}{!}
    % {\\begin{minipage}{1.1\textwidth}
    
    \centering   
    \caption{{}}   
    \label{table:}      
    
    \\begin{tabular}{lrrrrrrrr}     % 2 columns 
    
    \hline\hline  \\noalign{\\vskip 0.7mm}      
    '''
    
     
        text = text + '''Parameter \hspace{0.0 mm}'''
        for i in range(obj.npl):     
            text = text + '''& Planet %s '''%chr(98+i)
        text = text + '''\\\\
    \hline \\noalign{\\vskip 0.7mm} 
        
        '''
    
        text = text + '''{0:{width}s}'''.format("$K$  [m\,s$^{-1}$]", width = 30)
        for i in range(obj.npl):     
            text = text + '''& {0:{width}.{precision}f}$_{{-{1:{width2}.{precision}f}}}^{{+{2:{width2}.{precision}f}}}$ '''.format(obj.params.planet_params[7*i], obj.param_errors.planet_params_errors[7*i][0], obj.param_errors.planet_params_errors[7*i][1], width = width, width2 = 0, precision = precision)
        text = text + '''\\\\ \\noalign{\\vskip 0.9mm}
        '''        
        text = text + '''{0:{width}s}'''.format("$P$  [day]", width = 30)
        for i in range(obj.npl):     
            text = text + '''& {0:{width}.{precision}f}$_{{-{1:{width2}.{precision}f}}}^{{+{2:{width2}.{precision}f}}}$ '''.format(obj.params.planet_params[7*i +1], obj.param_errors.planet_params_errors[7*i +1][0], obj.param_errors.planet_params_errors[7*i +1][1], width = width, width2 = 0, precision = precision)
        text = text + '''\\\\ \\noalign{\\vskip 0.9mm}
        '''  
        text = text + '''{0:{width}s}'''.format("$e$  ", width = 30)
        for i in range(obj.npl):     
            text = text + '''& {0:{width}.{precision}f}$_{{-{1:{width2}.{precision}f}}}^{{+{2:{width2}.{precision}f}}}$ '''.format(obj.params.planet_params[7*i +2], obj.param_errors.planet_params_errors[7*i +2][0], obj.param_errors.planet_params_errors[7*i +2][1], width = width, width2 = 0, precision = precision)
        text = text + '''\\\\ \\noalign{\\vskip 0.9mm}
        '''  
        text = text + '''{0:{width}s}'''.format("$\omega$  [deg]", width = 30)
        for i in range(obj.npl):     
            text = text + '''& {0:{width}.{precision}f}$_{{-{1:{width2}.{precision}f}}}^{{+{2:{width2}.{precision}f}}}$ '''.format(obj.params.planet_params[7*i +3], obj.param_errors.planet_params_errors[7*i +3][0], obj.param_errors.planet_params_errors[7*i +3][1], width = width, width2 = 0, precision = precision)
        text = text + '''\\\\ \\noalign{\\vskip 0.9mm}
        '''  
        text = text + '''{0:{width}s}'''.format("$M_{\\rm 0}$  [deg]", width = 30)
        for i in range(obj.npl):     
            text = text + '''& {0:{width}.{precision}f}$_{{-{1:{width2}.{precision}f}}}^{{+{2:{width2}.{precision}f}}}$ '''.format(obj.params.planet_params[7*i +4], obj.param_errors.planet_params_errors[7*i +4][0], obj.param_errors.planet_params_errors[7*i +4][1], width = width, width2 = 0, precision = precision)
        text = text + '''\\\\ \\noalign{\\vskip 0.9mm}
        '''          
        text = text + '''{0:{width}s}'''.format("$i$  [deg]", width = 30)
        for i in range(obj.npl):     
            text = text + '''& {0:{width}.{precision}f}$_{{-{1:{width2}.{precision}f}}}^{{+{2:{width2}.{precision}f}}}$ '''.format(obj.params.planet_params[7*i +5], obj.param_errors.planet_params_errors[7*i +5][0], obj.param_errors.planet_params_errors[7*i +5][1], width = width, width2 = 0, precision = precision)
        text = text + '''\\\\ \\noalign{\\vskip 0.9mm} 
        '''      
        text = text + '''{0:{width}s}'''.format("$\Omega$  [deg]", width = 30)
        for i in range(obj.npl):     
            text = text + '''& {0:{width}.{precision}f}$_{{-{1:{width2}.{precision}f}}}^{{+{2:{width2}.{precision}f}}}$ '''.format(obj.params.planet_params[7*i +6], obj.param_errors.planet_params_errors[7*i +6][0], obj.param_errors.planet_params_errors[7*i +6][1], width = width, width2 = 0, precision = precision)
        text = text + '''\\\\ \\noalign{\\vskip 0.9mm} 
        '''            
        text = text + '''{0:{width}s}'''.format("$t_{\\rm 0}$  [day]", width = 30)
        for i in range(obj.npl):     
            text = text + '''& {0:{width}.{precision}f}$_{{-{1:{width2}.{precision}f}}}^{{+{2:{width2}.{precision}f}}}$ '''.format(obj.t0[i], obj.t0_err[i][0], obj.t0_err[i][1], width = width, width2 = 0, precision = precision)
        text = text + '''\\\\ \\noalign{\\vskip 0.9mm} 
        '''            
        text = text + '''{0:{width}s}'''.format("Rad.  [$R_\oplus$]", width = 30)
        for i in range(obj.npl):     
            text = text + '''& {0:{width}.{precision}f}$_{{-{1:{width2}.{precision}f}}}^{{+{2:{width2}.{precision}f}}}$ '''.format(obj.pl_rad[i], obj.pl_rad_err[i][0], obj.pl_rad_err[i][1], width = width, width2 = 0, precision = precision)            
        text = text + '''\\\\ \\noalign{\\vskip 0.9mm} 
        '''            
        text = text + '''{0:{width}s}'''.format("$a$  [$R_\odot$]", width = 30)
        for i in range(obj.npl):     
            text = text + '''& {0:{width}.{precision}f}$_{{-{1:{width2}.{precision}f}}}^{{+{2:{width2}.{precision}f}}}$ '''.format(obj.pl_a[i], obj.pl_a_err[i][0], obj.pl_a_err[i][1], width = width, width2 = 0, precision = precision)                        
        text = text + '''\\\\ \\noalign{\\vskip 0.9mm} 
        '''   
        text = text + '''{0:{width}s}'''.format("$a$  [au]", width = 30)
        for i in range(obj.npl):     
            text = text + '''& {0:{width}.{precision}f}$_{{-{1:{width2}.{precision}f}}}^{{+{2:{width2}.{precision}f}}}$ '''.format(obj.fit_results.a[i], 0,0, width = width, width2 = 0, precision = precision)                                    
        text = text + '''\\\\ \\noalign{\\vskip 0.9mm} 
        '''      
        text = text + '''{0:{width}s}'''.format("$m \sin i$  [$M_{\\rm jup}$]", width = 30)
        for i in range(obj.npl):     
            text = text + '''& {0:{width}.{precision}f}$_{{-{1:{width2}.{precision}f}}}^{{+{2:{width2}.{precision}f}}}$ '''.format(obj.fit_results.mass[i], 0,0, width = width, width2 = 0, precision = precision)                                                
        text = text + '''\\\\ \\noalign{\\vskip 0.9mm} 
        '''          
        text = text + '''{0:{width}s}'''.format("$t_{\omega}$  [day]", width = 30)
        for i in range(obj.npl):    
            text = text + '''& {0:{width}.{precision}f}$_{{-{1:{width2}.{precision}f}}}^{{+{2:{width2}.{precision}f}}}$ '''.format((float(obj.epoch) - (np.radians(obj.params.planet_params[7*i + 4])/(2*np.pi))*obj.params.planet_params[7*i + 1] ), 0,0, width = width, width2 = 0, precision = precision)                                                            
        text = text + '''\\\\ \\noalign{\\vskip 0.9mm} 
        '''          
     
             
        for i in range(obj.filelist.ndset):   
            text = text + '''{0:{width}s}'''.format("RV$_{\\rm off}$ %s"%(i+1), width = 30)      
            text = text + '''& {0:{width}.{precision}f}$_{{-{1:{width2}.{precision}f}}}^{{+{2:{width2}.{precision}f}}}$ '''.format(float(obj.params.offsets[i]), obj.param_errors.offset_errors[i][0], obj.param_errors.offset_errors[i][1], width = width, width2 = 0, precision = precision)                        
            text = text + '''\\\\ \\noalign{\\vskip 0.9mm}
        '''   
        for i in range(obj.filelist.ndset):   
            text = text + '''{0:{width}s}'''.format("RV$_{\\rm jit}$ %s"%(i+1), width = 30) 
            text = text + '''& {0:{width}.{precision}f}$_{{-{1:{width2}.{precision}f}}}^{{+{2:{width2}.{precision}f}}}$ '''.format(float(obj.params.jitters[i]), obj.param_errors.jitter_errors[i][0], obj.param_errors.jitter_errors[i][1], width = width, width2 = 0, precision = precision)                        
            text = text + '''\\\\ \\noalign{\\vskip 0.9mm}
        '''   
    
        text = text + '''{0:{width}s}'''.format("$\chi^2$", width = 30)            
        text = text + '''& {0:{width}.{precision}f} '''.format(float(obj.fit_results.chi2), width = width, precision = precision)
        text = text + '''\\\\
        '''    
        text = text + '''{0:{width}s}'''.format("$\chi_{\\nu}^2$", width = 30)            
        text = text + '''& {0:{width}.{precision}f} '''.format(float(obj.fit_results.reduced_chi2), width = width, precision = precision)
        text = text + '''\\\\
        '''        
        text = text + '''{0:{width}s}'''.format("$r.m.s.$ [m\,s$^{-1}$]", width = 30)            
        text = text + '''& {0:{width}.{precision}f} '''.format(float(obj.fit_results.rms), width = width, precision = precision)
        text = text + '''\\\\
        '''            
    
        text = text + '''{0:{width}s}'''.format("$-\ln\mathcal{L}$", width = 30)            
        text = text + '''& {0:{width}.{precision}f} '''.format(float(obj.fit_results.loglik), width = width, precision = precision)
        text = text + '''\\\\
        '''        
        text = text + '''{0:{width}s}'''.format("N$_{\\rm RV}$ data", width = 30)            
        text = text + '''& {0:{width}.{precision}f} '''.format(len(obj.fit_results.jd), width = width, precision = 0)
        text = text + '''\\\\
        '''         
        
        text = text + '''{0:{width}s}'''.format("Epoch", width = 30)            
        text = text + '''& {0:{width}.{precision}f} '''.format(obj.epoch, width = width, precision = precision)
        text = text + '''\\\\
        '''           
        
        text = text + '''\\\\
    \hline \\noalign{\\vskip 0.7mm} 
        
        '''     
        
        text = text + '''        
    \end{tabular}  
    
    % \end{minipage}}
    % \end{adjustwidth}
    
    %\\tablefoot{\small }
    
    \end{table}
    '''         

    else:
        print("asymmetric must be True or False")
        return
    
    
    table_file = open(file_name, 'wb') 
        
    table_file.write(text)
 
    table_file.close()


    return "Done"



def f_test(obj, obj2 = None, alpha = 0.01):


    chi2 = obj.fit_results.chi2
    ndata = len(obj.fit_results.jd)
    par2 = obj.fit_results.mfit      
   #     self.value_reduced_chi2.setText("%.4f"%(fit.fit_results.reduced_chi2))        
        #self.value_loglik.setText("%.4f"%(fit.fit_results.loglik)) 
   #     self.value_loglik.setText("%.4f"%(fit.loglik)) 
       

    if obj2 == None:
        obj2 = dill.copy(obj) 
        obj2.npl = 0
        obj2.fitting()
    else:
        obj2 = dill.copy(obj2) 

        if len(obj.fit_results.jd) != len(obj2.fit_results.jd):
            print("not the same data, test make no sense")
            return
 
    
    chi1 = obj2.fit_results.chi2
    par1 = obj2.fit_results.mfit      
    
    print(chi2,par1)
    #chi1_red = chi1/(ndata - par1)
    chi2_red = chi2/(ndata - par2)
    
     
    #raw_input("chi1_red = %s, Press Enter to continue <Enter>"%chi1_red)
    #F = (chi1 - chi2)/chi2_red
    
    F = ((chi1 - chi2)/(par2-par1))/chi2_red
    
     
    #raw_input("alpha = %s, Press Enter to continue <Enter>"%alpha)
    #print F, chi1_red, chi2_red
    
    p_value = pdf.f.sf(F, par2 - par1, ndata - par2, loc=0, scale=1) 
 


    print("""
\chi^2 null model = %s
\chi^2 tested model = %s
N parametrs null model = %s
N parametrs tested model = %s
F value = %s
p-value = %s
alpha value = %s
"""%(chi1,chi2,par1,par2,F,p_value,alpha))
    
    
    if float(p_value) < alpha:
    	print("Null hypothesis rejected")
    	print("Probability = ", (1.0-float(p_value))*100.0,'%')
    else:
    	print("Null hypothesis cannot be rejected")    




















