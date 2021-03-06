"""
Created on Mon Mar 23 15:51:39 2020

@author: Rabi Chhantyal-Pun
email: rcpchem@gmail.com, rc13564@bristol.ac.uk
Please use for only non-commerical use 
"""

from tkinter import *
from tkinter import messagebox
from tkinter import simpledialog
import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import odeint
from tkinter import filedialog
from lmfit import Model, Parameters, minimize, fit_report
import matplotlib.backends.backend_tkagg
from datetime import datetime
from scipy.integrate import solve_ivp
import sympy as sym

#function for generating ordinary differential equations
def rxn_ode(RRX,SSX):
#    unimolecular and bimolecular reactions    
#    R_A=[]*len(R) 
#    for i in range(len(R)):
#        if R[i].index('=') == 3:
#            AA=R[i][len(R[i])-1]+str('*')+R[i][0]+str('*')+R[i][2]
#        elif R[i].index('=') == 1:
#            AA=R[i][len(R[i])-1]+str('*')+R[i][0]
#        R_A.append(AA)
    
    #Reactions of all molecularity
    R_A=[]*len(RRX)
    for i in range(len(RRX)):
        R_A_i=[]*(len(RRX[i][0:RRX[i].index('=')])-RRX[i][0:RRX[i].index('=')].count('+')+1) #list for reaction species and k
        R_A_i.append(RRX[i][len(RRX[i])-1])
        for j in range(len(RRX[i][0:RRX[i].index('=')])-RRX[i][0:RRX[i].index('=')].count('+')):
            R_A_i.append('*'+RRX[i][j+j])
        R_A.append(''.join(R_A_i))
 
    #Combination of rate expression to give ode for all species           
    Sdt=[]*len(SSX)     
    for j in range(len(SSX)):
        Sdt_R=[]*len(RRX)
        for k in range(len(RRX)):
            if SSX[j] not in RRX[k]:
                continue
            for l in range(len(RRX[k])):
                if RRX[k][l]==SSX[j] and l < RRX[k].index('='):
                    Sdt_R.append('-'+R_A[k])
                elif RRX[k][l]==SSX[j] and l > RRX[k].index('='):
                    Sdt_R.append('+'+R_A[k])
        Sdt.append(Sdt_R)                               
    Sdt = [''.join(x) for x in Sdt]
    return(Sdt)
    
    
def box_model_callback():
    
    root.filename=filedialog.askopenfilename(initialdir='/Documents/Python', title='Select a file')
    file = open(root.filename,mode='r')
    all_of_it = file.read()
    file.close()
    
    all_of_it=all_of_it.split('\n\n')
    rxn_list=all_of_it[0]
    species_list=all_of_it[1]
    initial_C0_params=all_of_it[2]
    initial_k_params=all_of_it[3]
    plot_species_names=all_of_it[4]
    time_int=all_of_it[5]
    
    rxn_list=rxn_list.split('\n')
    del rxn_list[0]
    '\n'.join(rxn_list)

    
    species_list=species_list.split('\n')
    del species_list[0]
    species_list=''.join(species_list)
    SSX=species_list.split(':')
    
    initial_C0_params=initial_C0_params.split('\n')
    del initial_C0_params[0]
    initial_C0_params=''.join(initial_C0_params)
    
    initial_k_params=initial_k_params.split('\n')
    del initial_k_params[0]
    initial_k_params=''.join(initial_k_params)
    initial_k_params=initial_k_params.split(':')
    initial_k_params=[float(x) for x in initial_k_params]

    initial_C0_params=[float(x) for x in initial_C0_params.split(':')]
    
    time_int=time_int.split('\n')
    del time_int[0]
    time_int=time_int[0]
    time_int=time_int.split(':')
    
#    t=np.linspace(float(time_start_entry.get()),float(step_size_entry.get()),int(step_num_entry.get()))
    t=np.linspace(float(time_int[0]),float(time_int[1]),int(time_int[2]))
    
    rxn_list_split=rxn_list
    RRX=[]*len(rxn_list_split)
    for i in range(len(rxn_list_split)):
        R_i=rxn_list_split[i].split()
        RRX.append(R_i)
        
    

    def rxn(t,Conc):        
        #Dictionary for assigning species strings to concentrations 
        conc_dict={}
        for i in range(len(SSX)):
            conc_dict[SSX[i]]=Conc[i]
        for key,val in conc_dict.items():
            exec(key + '=val')
        
        #Dictionary for assigning parameter strings to parameter values         
        params=[]*len(RRX)
        for j in range(len(RRX)):
            params.append(RRX[j][len(RRX[j])-1])
        params_dict={}
        for k in range(len(params)):
            params_dict[params[k]]=initial_k_params[k]
        for key,val in params_dict.items():
            exec(key + '=val')

        Sdt = rxn_ode(RRX,SSX)
        Sdt_eval=[]*len(Sdt)
        for x in range(len(Sdt)):
            Sdt_eval.append(eval(Sdt[x]))
        return Sdt_eval        
    
    
    #analytical jacobain using sympy for solve_ivp
    total_species=len(SSX)
    C=sym.symbols('C:'+str(total_species))
    cdot_ivp=rxn(None,C)
    J_ivp=sym.Matrix(cdot_ivp).jacobian(C)
    t_sym = sym.symbols('t')
    f = sym.lambdify((t_sym, C) , cdot_ivp)
    J_jb_ivp=sym.lambdify((t_sym, C) , J_ivp)
    
#    (Conc,d)=odeint(rxn,initial_C0_params,t,full_output=1,mxordn=100, mxords=1000)
    Conc_int=solve_ivp(rxn,[time_int[0],time_int[1]],initial_C0_params,t_eval=t,method='LSODA',jac=J_jb_ivp)
#    print("Number of solve_ivp function evaluations: %d, number of solve_ivp Jacobian evaluations: %d" % (Conc_int.nfev, Conc_int.njev))
    plot_species_names=plot_species_names.split('\n')
    del plot_species_names[0]
    'n'.join(plot_species_names)
#    plot_species_names=plot_species_names[0]
    
    plot_S=plot_species_names[0]
#    print(plot_S)
    
#    plot_S=plot_species_entry.get()
    plot_S=plot_S.split(':')
    plot_S_num=[SSX.index(x) for x in plot_S]

    #Plotting modelled and exp data 
    exp=measured_species_entry.get()
    exp_names=exp.split(':')
    t=Conc_int.t
    Conc=Conc_int.y
    if exp == 'None':
        fig = plt.figure()
        ax = fig.add_subplot(111)
        for i in range(len(plot_S)):
            ax.plot(t,Conc[plot_S_num[i]],label=plot_S[i])
            plt.ylabel('[Concentration] (Unit)',fontsize=15)
            plt.xlabel('Time (s)',fontsize=15)
            plt.legend()
    else:
        root.filename=filedialog.askopenfilename(initialdir='/Documents/Python', title='Select a file')
        data=np.genfromtxt(root.filename)
        fig = plt.figure()
        ax = fig.add_subplot(111)
        for i in range(len(plot_S)):
            ax.plot(t,Conc[:,plot_S_num[i]],label=plot_S[i])
            plt.ylabel('[Concentration] (Unit)',fontsize=15)
            plt.xlabel('Time (s)',fontsize=15)
            plt.legend()
        for j in range(len(data[0,:])-1):
            ax.plot(data[:,0],data[:,j+1],label='Exp '+exp_names[j])
            plt.ylabel('[Concentration] (Unit)',fontsize=15)
            plt.xlabel('Time (s)',fontsize=15)
            plt.legend()   
    
    #saving model results and log
    response = messagebox.askquestion('Save?','Do you want to save file?')
    if response == 'yes':
        fname=simpledialog.askstring('Filename', 'Please enter filename')
#        np.savetxt(fname+'.txt', np.hstack((t,Conc)), delimiter="\t", fmt='%s')
        np.savetxt(fname+'.txt', np.hstack((t.reshape(len(t),1),Conc.transpose())), delimiter="\t", fmt='%s')
    plt.show()

def model_exp_callback():

    initial_C0_params=initial_C0_params_entry.get()
    initial_C0_params=[float(x) for x in initial_C0_params.split(':')]
    time_start=float(time_start_entry.get())
    time_stop=float(step_size_entry.get())
    steps=int(step_num_entry.get())

    t=np.linspace(time_start,time_stop,steps)
    
    rxn_list=rxn_textbox.get("1.0","end-1c")
    rxn_list_split=rxn_list.split('\n')
    RRX=[]*len(rxn_list_split)
    for i in range(len(rxn_list_split)):
        R_i=rxn_list_split[i].split()
        RRX.append(R_i)
    
    species_list=species_entry.get()
    SSX=species_list.split(':')   

    def rxn(t,Conc):        
        #Dictionary for assigning species strings to concentrations 
        conc_dict={}
        for i in range(len(SSX)):
            conc_dict[SSX[i]]=Conc[i]
        for key,val in conc_dict.items():
            exec(key + '=val')
        
        #Dictionary for assigning parameter strings to parameter values         
        initial_k_params=initial_k_params_entry.get()
        initial_k_params=initial_k_params.split(':')
        initial_k_params=[float(x) for x in initial_k_params]
        params=[]*len(RRX)
        for j in range(len(RRX)):
            params.append(RRX[j][len(RRX[j])-1])
        params_dict={}
        for k in range(len(params)):
            params_dict[params[k]]=initial_k_params[k]
        for key,val in params_dict.items():
            exec(key + '=val')

        Sdt = rxn_ode(RRX,SSX)
        Sdt_eval=[]*len(Sdt)
        for x in range(len(Sdt)):
            Sdt_eval.append(eval(Sdt[x]))
        return Sdt_eval       
    
    #analytical jacobain using sympy for solve_ivp
    total_species=len(SSX)
    C=sym.symbols('C:'+str(total_species))
    cdot_ivp=rxn(None,C)
    J_ivp=sym.Matrix(cdot_ivp).jacobian(C)
    t_sym = sym.symbols('t')
    f = sym.lambdify((t_sym, C) , cdot_ivp)
    J_jb_ivp=sym.lambdify((t_sym, C) , J_ivp)
        
    Conc_int=solve_ivp(rxn,[time_start,time_stop],initial_C0_params,t_eval=t,method='LSODA',jac=J_jb_ivp)
#    print("Number of solve_ivp function evaluations: %d, number of solve_ivp Jacobian evaluations: %d" % (Conc_int.nfev, Conc_int.njev))
    
    plot_S=plot_species_entry.get()
    plot_S=plot_S.split(':')
    plot_S_num=[SSX.index(x) for x in plot_S]

    #Plotting modelled and exp data       
    exp=measured_species_entry.get()
    exp_names=exp.split(':')
    t=Conc_int.t
    Conc=Conc_int.y
    if exp == 'None':
        fig = plt.figure()
        ax = fig.add_subplot(111)
        for i in range(len(plot_S)):
            ax.plot(t,Conc[plot_S_num[i]],label=plot_S[i])
            plt.ylabel('[Concentration] (Unit)',fontsize=15)
            plt.xlabel('Time (s)',fontsize=15)
            plt.legend()
    else:
        root.filename=filedialog.askopenfilename(initialdir='/Documents/Python', title='Select a file')
        data=np.genfromtxt(root.filename)
        fig = plt.figure()
        ax = fig.add_subplot(111)
        for i in range(len(plot_S)):
            ax.plot(t,Conc[plot_S_num[i]],label=plot_S[i])
            plt.ylabel('[Concentration] (Unit)',fontsize=15)
            plt.xlabel('Time (s)',fontsize=15)
            plt.legend()
        for j in range(len(data[0,:])-1):
            ax.plot(data[:,0],data[:,j+1],label='Exp '+exp_names[j])
            plt.ylabel('[Concentration] (Unit)',fontsize=15)
            plt.xlabel('Time (s)',fontsize=15)
            plt.legend()   
    
    #saving model results and log 
    response = messagebox.askquestion('Save?','Do you want to save file?')
    if response == 'yes':
        fname=simpledialog.askstring('Filename', 'Please enter filename')
        np.savetxt(fname+'.txt', np.column_stack((t,Conc)), delimiter="\t", fmt='%s')
        
        
        log_file='Reaction Model\n'+rxn_list+'\n\n'
        log_file=log_file+'Reactions Species\n'+species_entry.get()+'\n\n'
        log_file=log_file+'Initial Concentrations\n'+initial_C0_params_entry.get()+'\n\n'
        log_file=log_file+'Rate Coefficient Values\n'+initial_k_params_entry.get()+'\n\n'
        log_file=log_file+'Successful run at '+str(datetime.now())
        f = open(fname+'_log.txt', 'w')
        f.write(log_file) 
        f.close()
    plt.show()


def fit_callback():
    
    exp=measured_species_entry.get()
    S_m=exp.split(':')
    
    if exp == 'None':
        print('Give Measured Species labels')
        return
    del exp
    
    #Experimental data input
    root.filename=filedialog.askopenfilename(initialdir='/Documents/Python', title='Select a file')
    data=np.genfromtxt(root.filename)
    
    #Experimental time measurement
    t=data[:,0]
    time_start=t[0]
    time_stop=t[len(t)-1]

    #dictionatory for measured signals
    sig_dic={}    
    for i in range(len(S_m)):
        sig_dic[S_m[i]]=data[:,i+1]

    
    #Reaction Model and Species from user input    
    rxn_list=rxn_textbox.get("1.0","end-1c")
    rxn_list_split=rxn_list.split('\n')
    RRX=[]*len(rxn_list_split)
    for i in range(len(rxn_list_split)):
        R_i=rxn_list_split[i].split()
        RRX.append(R_i)
    
    #List of species from user input
    species_list=species_entry.get()
    SSX=species_list.split(':')

    #Packing Parameters for lmfit module
    initial_k_params=initial_k_params_entry.get()
    initial_k_params=initial_k_params.split(':')
    initial_k_params=[float(x) for x in initial_k_params] 
    min_k_params=min_k_params_entry.get()
    min_k_params=min_k_params.split(':')
    min_k_params=[float(x) for x in min_k_params]
    max_k_params=max_k_params_entry.get()
    max_k_params=max_k_params.split(':')
    max_k_params=[float(x) for x in max_k_params]
    
    initial_C0_params=initial_C0_params_entry.get()
    initial_C0_params=initial_C0_params.split(':')
    initial_C0_params=[float(x) for x in initial_C0_params]
    min_C0_params=min_C0_params_entry.get()
    min_C0_params=min_C0_params.split(':')
    min_C0_params=[float(x) for x in min_C0_params]
    max_C0_params=max_C0_params_entry.get()
    max_C0_params=max_C0_params.split(':')
    max_C0_params=[float(x) for x in max_C0_params]
    
    
    #vary or fix parameters?
    kk=[]*len(max_k_params)
    for tt in range(len(min_k_params)):
        if min_k_params[tt]==max_k_params[tt]:
            kk.append('false')
        else:
            kk.append('true')
    del tt
    
    cc=[]*len(max_C0_params)
    for tt in range(len(min_C0_params)):
        if min_C0_params[tt]==max_C0_params[tt]:
            cc.append('false')
        else:
            cc.append('true')
    del tt
   
    #Collection of rate and concentration parameter from reaction model input for fitting
    params = Parameters()
    params_names=[]*len(RRX)
    for l in range(len(RRX)):
        params_names.append(RRX[l][len(RRX[l])-1])
    del l

    for p in range(len(params_names)):
        if kk[p]=='true':
            params.add(str(params_names[p]), value=initial_k_params[p], min=min_k_params[p], max=max_k_params[p])
        elif kk[p]=='false':
            params.add(str(params_names[p]), value=initial_k_params[p], vary=False)
    del p
    
    species_names=species_entry.get()
    species_names=species_names.split(':')
    species_names=['Initial_' + s for s in species_names]
    
    for p in range(len(species_names)):
        if cc[p]=='true':
            params.add(species_names[p], value=initial_C0_params[p], min=min_C0_params[p], max=max_C0_params[p])
        elif cc[p]=='false':
            params.add(species_names[p], value=initial_C0_params[p], vary=False)
    del p
    
    def rxn_fit(params,t,sig_dic):      
        
        def rxn(t,Conc):  
            
            #Relating params values to rate coefficient labels in the model   
            params_dict={}
            for k in range(len(params_names)):
                params_dict[params_names[k]]=params[params_names[k]]
            for key,val in params_dict.items():
                exec(key + '=val')
            
            #Relating Conc values to S labels in the model        
            conc_dict={}
            for i in range(len(SSX)):
                conc_dict[SSX[i]]=Conc[i]
            for key,val in conc_dict.items():
                exec(key + '=val')
    
            Sdt=rxn_ode(RRX,SSX)
            Sdt_eval=[]*len(Sdt)
            for x in range(len(Sdt)):
                Sdt_eval.append(eval(Sdt[x]))
            return Sdt_eval
        
        #list of initial concentration values for all the reaction species 
        C0=[]*len(species_names)
        for p in range(len(species_names)):
            conc=params[species_names[p]]
            C0.append(conc)
               
        #analytical jacobain using sympy for solve_ivp
        total_species=len(SSX)
        C=sym.symbols('C:'+str(total_species))
        cdot_ivp=rxn(None,C)
        J_ivp=sym.Matrix(cdot_ivp).jacobian(C)
        t_sym = sym.symbols('t')
        f = sym.lambdify((t_sym, C) , cdot_ivp)
        J_jb_ivp=sym.lambdify((t_sym, C) , J_ivp)
        
        Conc=solve_ivp(rxn,[time_start,time_stop],C0,t_eval=t,method='LSODA',jac=J_jb_ivp)
#        print("Number of solve_ivp function evaluations: %d, number of solve_ivp Jacobian evaluations: %d" % (Conc.nfev, Conc.njev))
        Conc=Conc.y
        residual=[]*len(S_m)
        for i in range(len(S_m)):
            residual.append(Conc[SSX.index(S_m[i])]-sig_dic[S_m[i]])
        return residual
    

    out = minimize(rxn_fit, params, args=(t, sig_dic), method='leastsq')
    print('Success!')
    print(fit_report(out.params)) 

    #Modelled concentration with optimized parameters
    def rxn_final(t,Conc):  
        
        #Relating Conc values to S labels in the model        
        conc_dict={}
        for i in range(len(SSX)):
            conc_dict[SSX[i]]=Conc[i]
        for key,val in conc_dict.items():
            exec(key + '=val')
              
        #Relating params values to rate coefficient labels in the model    
        out_params_dict={}
        for k in range(len(params_names)):
            out_params_dict[params_names[k]]=out.params[params_names[k]].value
        for key,val in out_params_dict.items():
            exec(key + '=val')
    
        Sdt=rxn_ode(RRX,SSX)
        Sdt_eval=[]*len(Sdt)
        for x in range(len(Sdt)):
            Sdt_eval.append(eval(Sdt[x]))
        return Sdt_eval   
     
    #list of initial concentration values for all the reaction species 
    C0=[]*len(species_names)
    for p in range(len(species_names)):
        conc=out.params[species_names[p]].value 
        C0.append(conc) 

    t1=np.linspace(np.min(t),np.max(t),np.int(step_num_entry.get())) 
    
    #analytical jacobain using sympy for solve_ivp
    total_species=len(SSX)
    C=sym.symbols('C:'+str(total_species))
    cdot_ivp=rxn_final(None,C)
    J_ivp=sym.Matrix(cdot_ivp).jacobian(C)
    t_sym = sym.symbols('t')
    f = sym.lambdify((t_sym, C) , cdot_ivp)
    J_jb_ivp=sym.lambdify((t_sym, C) , J_ivp)
#    Conc=odeint(rxn_final,C0,t1)   
    Conc=solve_ivp(rxn_final,[np.min(t),np.max(t)],C0,t_eval=t1,method='LSODA',jac=J_jb_ivp)
#    print("Number of solve_ivp function evaluations: %d, number of solve_ivp Jacobian evaluations: %d" % (Conc.nfev, Conc.njev))
    
    Conc=Conc.y
    #Plotting modelled and exp data       
    plot_S=plot_species_entry.get()
    plot_S=plot_S.split(':')
    plot_S_num=[SSX.index(x) for x in plot_S]
    
    fig = plt.figure()
    ax = fig.add_subplot(111)
    for i in range(len(plot_S)):
        ax.plot(t1,Conc[plot_S_num[i]],label='Fit Model '+plot_S[i])
        plt.ylabel('[Concentration] (Unit)',fontsize=15)
        plt.xlabel('Time (s)',fontsize=15)
        plt.legend()
    del i    
    for i in range(len(S_m)):
        ax.plot(t,sig_dic[S_m[i]],label='Exp '+S_m[i])
        plt.ylabel('[Concentration] (Unit)',fontsize=15)
        plt.xlabel('Time (s)',fontsize=15)
        plt.legend()
    del i 
   
    #saving model results and log   
    response = messagebox.askquestion('Save?','Do you want to save file?')
    if response == 'yes':
        fname=simpledialog.askstring('Filename', 'Please enter filename')
        np.savetxt(fname+'.txt', np.column_stack((t1,Conc)), delimiter="\t", fmt='%s')
        
        log_file='Successful run at '+str(datetime.now())+'\n'
        log_file=log_file+'\n'+'Reaction Model\n'+rxn_list+'\n'
        log_file=log_file+'Reactions Species\n'+species_entry.get()+'\n'
        log_file=log_file+'Initial Concentrations\n'+initial_C0_params_entry.get()+'\n'
        log_file=log_file+'Inital Rate Coefficient Values\n'+initial_k_params_entry.get()+'\n'
        log_file=log_file+'Min Initial Concentration Values\n'+min_C0_params_entry.get()+'\n'
        log_file=log_file+'Max Initial Concentration Values\n'+max_C0_params_entry.get()+'\n'
        log_file=log_file+'Min Rate Coefficient Values\n'+min_k_params_entry.get()+'\n'
        log_file=log_file+'Max Rate Coefficient Values\n'+max_k_params_entry.get()+'\n'
        log_file=log_file+'\n'+'Fit Result'+'\n'+str(fit_report(out.params))
        f = open(fname+'_log.txt', 'w')
        f.write(log_file)
        f.close()
    plt.show()   

root=Tk()

Label(root, text="Reaction Model").grid(row=0,column=0,padx=5,pady=5)
rxn_textbox=Text(root, width=30, height=10, padx=5)
rxn_textbox.insert('1.0', 'CH2OO + CH2OO = Product1 : k1\nCH2OO = Product2  : k2')
rxn_textbox.grid(row=0,column=0,columnspan=5,padx=5,pady=5)
#rxn=rxn_textbox.get("1.0","end-1c")

Label(root, text="Reaction Species").grid(row=5,column=0,padx=5,pady=5)
species_entry=Entry(root)
species_entry.insert(0,'CH2OO:Product1:Product2')
species_entry.grid(row=5,column=1,padx=5)

Label(root, text="Initial Concentrations, C0").grid(row=6,column=0,padx=5,pady=5)
initial_C0_params_entry=Entry(root)
initial_C0_params_entry.insert(0,'1E12:0:0')
initial_C0_params_entry.grid(row=6,column=1,padx=5)

Label(root, text="Initial Rate Coefficients, k").grid(row=7,column=0,padx=5,pady=5)
initial_k_params_entry=Entry(root)
initial_k_params_entry.insert(0,'1E-10:50')
initial_k_params_entry.grid(row=7,column=1,padx=5)

Label(root, text="Time Start").grid(row=8,column=0,padx=5,pady=5)
time_start_entry=Entry(root)
time_start_entry.insert(0, '0')
time_start_entry.grid(row=8,column=1,padx=5)

Label(root, text="Time Stop").grid(row=9,column=0,padx=5,pady=5)
step_size_entry=Entry(root)
step_size_entry.insert(0, '0.01')
step_size_entry.grid(row=9,column=1,padx=5)
#
Label(root, text="Number of Steps").grid(row=10,column=0,padx=5,pady=5)
step_num_entry=Entry(root)
step_num_entry.insert(0, '100')
step_num_entry.grid(row=10,column=1,padx=5)

Label(root, text="Measured Species").grid(row=5,column=3,padx=5,pady=5)
measured_species_entry=Entry(root)
measured_species_entry.insert(0,'None')
measured_species_entry.grid(row=5,column=4,padx=5)

Label(root, text="C0 min -Fit").grid(row=6,column=3,padx=5,pady=5)
min_C0_params_entry=Entry(root)
min_C0_params_entry.insert(0,'1E12:0:0')
min_C0_params_entry.grid(row=6,column=4,padx=5)

Label(root, text="C0 max -Fit").grid(row=7,column=3,padx=5,pady=5)
max_C0_params_entry=Entry(root)
max_C0_params_entry.insert(0,'1E13:0:0')
max_C0_params_entry.grid(row=7,column=4,padx=5)

Label(root, text="k min -Fit").grid(row=8,column=3,padx=5,pady=5)
min_k_params_entry=Entry(root)
min_k_params_entry.insert(0,'1E-11:10')
min_k_params_entry.grid(row=8,column=4,padx=5)

Label(root, text="k max -Fit").grid(row=9,column=3,padx=5,pady=5)
max_k_params_entry=Entry(root)
max_k_params_entry.insert(0,'1E-9:1000')
max_k_params_entry.grid(row=9,column=4,padx=5)

Label(root, text="Species to Plot").grid(row=10,column=3,padx=5,pady=5)
plot_species_entry=Entry(root)
plot_species_entry.insert(0,'CH2OO:Product1:Product2')
plot_species_entry.grid(row=10,column=4,padx=5)


file_button=Button(root,text='Fit',command=fit_callback)
file_button.config(height=3,width=15)
file_button.grid(row=11,column=4)

model_exp_button=Button(root,text='Model',command=model_exp_callback)
model_exp_button.config(height=3,width=15)
model_exp_button.grid(row=11,column=3)

box_model_button=Button(root,text='Box Model',command=box_model_callback)
box_model_button.config(height=3,width=15)
box_model_button.grid(row=11,column=1)

quit_button=Button(root, text="Quit", command=root.destroy)
quit_button.config(height=3,width=15)
quit_button.grid(row=11,column=0)

#root.deiconify()
root.mainloop()


    