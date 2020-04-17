"""
Created on Mon Mar 23 15:51:39 2020

@author: rc13564
"""

from tkinter import *
import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import odeint
from tkinter import filedialog
from lmfit import Model, Parameters, minimize, fit_report
import matplotlib.backends.backend_tkagg

root=Tk()

Label(root, text="Reaction Model").grid(row=0,column=0,padx=5,pady=5)
rxn_textbox=Text(root, width=30, height=10, padx=5)
rxn_textbox.insert('1.0', 'A + A = C + D : k1\nA + B = D  : k2')
rxn_textbox.grid(row=0,column=0,columnspan=5,padx=5,pady=5)
#rxn=rxn_textbox.get("1.0","end-1c")

Label(root, text="Reaction Species").grid(row=5,column=0,padx=5,pady=5)
species_entry=Entry(root)
species_entry.insert(0,'A:B:C:D')
species_entry.grid(row=5,column=1,padx=5)

Label(root, text="Initial Concentrations").grid(row=6,column=0,padx=5,pady=5)
conc_entry=Entry(root)
conc_entry.insert(0,'1E12:1E12:0:0')
conc_entry.grid(row=6,column=1,padx=5)

Label(root, text="Time Start").grid(row=7,column=0,padx=5,pady=5)
time_start_entry=Entry(root)
time_start_entry.insert(0, '0')
time_start_entry.grid(row=7,column=1,padx=5)

Label(root, text="Time Step Size").grid(row=8,column=0,padx=5,pady=5)
step_size_entry=Entry(root)
step_size_entry.insert(0, '0.01')
step_size_entry.grid(row=8,column=1,padx=5)
#
Label(root, text="Number of Steps").grid(row=9,column=0,padx=5,pady=5)
step_num_entry=Entry(root)
step_num_entry.insert(0, '100')
step_num_entry.grid(row=9,column=1,padx=5)

Label(root, text="Species to Plot").grid(row=10,column=0,padx=5,pady=5)
plot_species_entry=Entry(root)
plot_species_entry.insert(0,'A:B:C:D')
plot_species_entry.grid(row=10,column=1,padx=5)

Label(root, text="Measured Species").grid(row=5,column=3,padx=5,pady=5)
measured_species_entry=Entry(root)
measured_species_entry.insert(0,'None')
measured_species_entry.grid(row=5,column=4,padx=5)

Label(root, text="Initial k").grid(row=6,column=3,padx=5,pady=5)
initial_params_entry=Entry(root)
initial_params_entry.insert(0,'1E-11:1E-11')
initial_params_entry.grid(row=6,column=4,padx=5)

Label(root, text="k min -Fit").grid(row=7,column=3,padx=5,pady=5)
min_params_entry=Entry(root)
min_params_entry.insert(0,'1E-11:1E-11')
min_params_entry.grid(row=7,column=4,padx=5)

Label(root, text="k max -Fit").grid(row=8,column=3,padx=5,pady=5)
max_params_entry=Entry(root)
max_params_entry.insert(0,'1E-11:1E-11')
max_params_entry.grid(row=8,column=4,padx=5)

    
def model_exp_callback():
    C0=conc_entry.get()
    C0=C0.split(':')  
    C0=[float(x) for x in C0]

    t=np.linspace(float(time_start_entry.get()),float(step_size_entry.get()),int(step_num_entry.get()))
    
    rxn_list=rxn_textbox.get("1.0","end-1c")
    rxn_list=rxn_list.split('\n')
    R=[]*len(rxn_list)
    for i in range(len(rxn_list)):
        R_i=rxn_list[i].split()
        R.append(R_i)
    
    species_list=species_entry.get()
    S=species_list.split(':')
    
        
    def rxn(Conc,t):        
        #Dictionary for assigning species strings to concentrations 
        conc_dict={}
        for i in range(len(S)):
            conc_dict[S[i]]=Conc[i]
        for key,val in conc_dict.items():
            exec(key + '=val')
        
        #Dictionary for assigning parameter strings to parameter values         
        initial_params=initial_params_entry.get()
        initial_params=initial_params.split(':')
        initial_params=[float(x) for x in initial_params]
        params=[]*len(R)
        for j in range(len(R)):
            params.append(R[j][len(R[j])-1])
        params_dict={}
        for k in range(len(params)):
            params_dict[params[k]]=initial_params[k]
        for key,val in params_dict.items():
            exec(key + '=val')


#        rate expression for reactants for all reactions
#        unimolecular and bimolecular reactions    
#        R_A=[]*len(R) 
#        for i in range(len(R)):
#            if R[i].index('=') == 3:
#                AA=R[i][len(R[i])-1]+str('*')+R[i][0]+str('*')+R[i][2]
#            elif R[i].index('=') == 1:
#                AA=R[i][len(R[i])-1]+str('*')+R[i][0]
#            R_A.append(AA)
        #Reactions of all molecularity
        R_A=[]*len(R)
        for i in range(len(R)):
            R_A_i=[]*(len(R[i][0:R[i].index('=')])-R[i][0:R[i].index('=')].count('+')+1) #list for reaction species and k
            R_A_i.append(R[i][len(R[i])-1])
            for j in range(len(R[i][0:R[i].index('=')])-R[i][0:R[i].index('=')].count('+')):
                R_A_i.append('*'+R[i][j+j])
            R_A.append(''.join(R_A_i))
 
        #Combination of rate expression to give ode for all species           
        Sdt=[]*len(S)     
        for j in range(len(S)):
            Sdt_R=[]*len(R)
            for k in range(len(R)):
                if S[j] not in R[k]:
                    continue
                for l in range(len(R[k])):
                    if R[k][l]==S[j] and l < R[k].index('='):
                        Sdt_R.append('-'+R_A[k])
                    elif R[k][l]==S[j] and l > R[k].index('='):
                        Sdt_R.append('+'+R_A[k])
            Sdt.append(Sdt_R)                               
        Sdt = [''.join(x) for x in Sdt]
        Sdt_eval=[]*len(Sdt)
        for x in range(len(Sdt)):
            Sdt_eval.append(eval(Sdt[x]))
        return Sdt_eval        
        
    Conc=odeint(rxn,C0,t)
    
#    Simulating noisy signal 
#    noise1 = np.random.normal(0, 1E10, len(Conc[:,0]))
#    noisy_sig1=Conc[:,0]+noise1
#    noise2 = np.random.normal(0, 1E10, len(Conc[:,0]))
#    noisy_sig2=Conc[:,2]+noise2
#    np.savetxt("file_name.txt", np.column_stack((t,noisy_sig1,noisy_sig2)), delimiter="\t", fmt='%s')
    
    plot_S=plot_species_entry.get()
    plot_S=plot_S.split(':')
    plot_S_num=[S.index(x) for x in plot_S]

    #Plotting modelled and exp data       
    exp=measured_species_entry.get()
    exp_names=exp.split(':')
    if exp == 'None':
        fig = plt.figure()
        ax = fig.add_subplot(111)
        for i in range(len(plot_S)):
            ax.plot(t,Conc[:,plot_S_num[i]],label=plot_S[i])
            plt.ylabel('[Concentration] (Unit)',fontsize=15)
            plt.xlabel('Time (s)',fontsize=15)
            plt.legend()
    else:
        root.filename=filedialog.askopenfilename(initialdir='/Documents/Python', title='Select a file')
        data=np.genfromtxt(root.filename)
        fig = plt.figure()
        ax = fig.add_subplot(111)
        for j in range(len(data[0,:])-1):
            ax.plot(data[:,0],data[:,j+1],label='Exp '+exp_names[j])
            plt.ylabel('[Concentration] (Unit)',fontsize=15)
            plt.xlabel('Time (s)',fontsize=15)
            plt.legend()
        for i in range(len(plot_S)):
            ax.plot(t,Conc[:,plot_S_num[i]],label=plot_S[i])
            plt.ylabel('[Concentration] (Unit)',fontsize=15)
            plt.xlabel('Time (s)',fontsize=15)
            plt.legend()
    plt.show()
    print('Success!')
    
#file_button=Button(root,text='Fit',command=fit_callback)
#file_button.config(height=3,width=15)
#file_button.grid(row=11,column=4)

model_exp_button=Button(root,text='Model',command=model_exp_callback)
model_exp_button.config(height=3,width=15)
model_exp_button.grid(row=11,column=3)

quit_button=Button(root, text="Quit", command=root.destroy)
quit_button.config(height=3,width=15)
quit_button.grid(row=11,column=0)

root.mainloop()


    