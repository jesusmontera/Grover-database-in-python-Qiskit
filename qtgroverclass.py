from qiskit import *
import qiskit.quantum_info as qi
from qiskit.quantum_info import DensityMatrix,partial_trace

import math
import operator
import numpy as np

def cadenabinaria(x, n=0):    
    return format(x, 'b').zfill(n)
def reversed_string(a_string):
    return a_string[::-1]

class Grover:    
        
    def __init__(self):
        self.stateSearch = 0
        self.numexecutions=100
        self.m_resultado=[]        
        self.NOSEARCHING=0
        self.SEARCHING=1
        self.SEARCHCANCEL=2
        self.SEARCHENDED=3
        #self.statevector=qi.Statevector.from_instruction(self.qc)
        self.statevector=None
        self.qc = QuantumCircuit(9,9)
        self.funinfoend=None
        self.txout=""
        
    def Reset(self,numqbits, numexes):
        self.numqbits = numqbits        
        self.iqaux= numqbits -1
        self.qc = QuantumCircuit(numqbits,numqbits)
        #self.qc.reset([0,numqbits-1])
        self.m_resultado=[]
        self.stateSearch = 0
        self.txout=""
        self.numexecutions=numexes
        
    def GetResultList(self):
        return self.m_resultado    
    def GetQubitStateVector(self,indexqbit):
        #full_statevector = Statevector(circuit)
        # get the density matrix for the first qubit by taking the partial trace
        listout=[]
        for k in range(self.numqbits):
            if k != indexqbit:
                listout.append(k)
            
        partial_density_matrix = partial_trace(self.statevector, listout)
        # extract the statevector out of the density matrix
        partial_statevector = np.diagonal(partial_density_matrix)
        return partial_statevector
        
    def PrintPureza(self,sdescription):        
        rho = qi.DensityMatrix.from_instruction(self.qc)
        self.txout += sdescription + "\n"
        for i in range(self.numqbits):
            if self.stateSearch == 2: break
            purezaqbit = partial_trace(rho,[i]).purity()
            purezaqbit = np.round(np.abs(purezaqbit),3)
            self.txout +="\tpureza qbit " + str( i) + " = " + str(purezaqbit) + "\n"
            
##            if self.funout == None:
##                print("\tpureza qbit " , i, " = " ,purezaqbit)
##            else:
##                self.funout("\tpureza qbit " + str( i) + " = " + str(purezaqbit))

    def GetGroverIterarions(self,nStates,nSolutions):
        n= (math.pi / 4)
        d = math.sqrt(float(nStates)/nSolutions)
        gloops=n*d
        return math.floor(gloops)
    
    def ctrlArrayX(self,listacontrols,nbitsindex,targetbit,strbitindexs):        
        for i in range(nbitsindex):
            if strbitindexs[i] == '0':                
                self.qc.x(listacontrols[i])
        self.qc.mct(listacontrols,targetbit)
        
        for i in range(nbitsindex-1,-1,-1):
            if strbitindexs[i] == '0':
                self.qc.x(listacontrols[i])    
        
    def SetQRamDataBase(self,numregisters, nbitsindex, nbitsvalues, indexs, values):
        listacontrols = []
        for i in range(nbitsindex):
            listacontrols.append(i)
            
        for i in range(numregisters):
            strbitindexs= reversed_string(cadenabinaria(indexs[i],nbitsindex))
            strbitsvalues= reversed_string(cadenabinaria(values[i],nbitsvalues))            
            
            for k in range(nbitsvalues):
                
                if strbitsvalues[k] == '1':
                    targetbit = k + nbitsindex
                    self.ctrlArrayX(listacontrols,nbitsindex,targetbit,strbitindexs)
                                    
                    
    def Oracle(self,searchednums,nbitsindexs,nbitsval):
        idxcontrol = nbitsindexs
        listacontrols = []
        for y in range(nbitsval):
            listacontrols.append(idxcontrol + y)

        for k in range(len(searchednums)):
            searchvalbin = cadenabinaria(searchednums[k] , nbitsval)

            #activate qubits in value register
            for y in range(nbitsval):        
                if searchvalbin[(nbitsval-1)-y] == '0':            
                    self.qc.x(idxcontrol+y)
            self.qc.h(self.iqaux)
            self.qc.mct(listacontrols,self.iqaux)    
            self.qc.h(self.iqaux)
            #desactivate qubits in value register        
            for y in range(nbitsval):        
                if searchvalbin[(nbitsval-1)-y] == '0':            
                    self.qc.x(idxcontrol+y)            
            
    
    def Difusor(self,nbitsindex):
        listacontrols = []
        for i in range(nbitsindex):
            listacontrols.append(i)
        self.qc.h(range(nbitsindex))
        self.qc.x(range(nbitsindex))
        self.qc.h(self.iqaux)    
        self.qc.mct(listacontrols,self.iqaux)
        self.qc.h(self.iqaux)        
        self.qc.x(range(nbitsindex))
        self.qc.h(range(nbitsindex))    

    def ExecuteCircuit(self, ejecuciones):        
        backend = Aer.get_backend('qasm_simulator')        
        job = execute(self.qc, backend, shots = ejecuciones)
        # Grab the results from the job.
        result = job.result()
        diccount = result.get_counts(self.qc)
        return diccount
        
    
    def Search(self,searchedlist,indexs,values,bShowPurity):
        
        self.stateSearch=self.SEARCHING
        self.m_resultado=[]
        nbitsval=int(self.numqbits/2)
        nbitsindexs=int(self.numqbits/2)
        self.qc.h(range(nbitsindexs))
        self.qc.h(self.iqaux)         
        nregsdb= len(indexs)
        if bShowPurity: self.PrintPureza("pureza al inicio")
        self.SetQRamDataBase(nregsdb, nbitsindexs, nbitsval, indexs, values)
        if bShowPurity: self.PrintPureza("pureza tras SetQRamDataBase")
        #repetir N veces segun grover loops
        nsolutions=len(searchedlist)
        nstates=int(2**nbitsindexs)
        nloopsgrover=self.GetGroverIterarions(nstates,nsolutions)
        for i in range(nloopsgrover):
            if self.stateSearch == 2: break
            if bShowPurity: self.txout +="inicio grover loop "+str(i+1) + " de " +  str(nloopsgrover)
                
            self.Oracle(searchedlist,nbitsindexs,nbitsval)    
            if self.stateSearch == 2: break
            if bShowPurity: self.PrintPureza("pureza tras oraculo ")    
            if self.stateSearch == 2: break
            self.SetQRamDataBase(nregsdb, nbitsindexs, nbitsval, indexs, values)
            if self.stateSearch == 2: break
            if bShowPurity: self.PrintPureza("pureza tras SetQRamDataBase")
            if self.stateSearch == 2: break
            self.Difusor(nbitsindexs)
            if self.stateSearch == 2: break
            if bShowPurity: self.PrintPureza("pureza tras difusor")
            if bShowPurity: self.txout +="fin grover loop " + str(i+1)+ " de " +str(  nloopsgrover)
        #save state vector for plot bloch
        self.statevector = qi.Statevector.from_instruction(self.qc)
        
        self.qc.measure(range(nbitsindexs), range(nbitsindexs))
        diccount = self.ExecuteCircuit(self.numexecutions)
        dictuple = sorted(diccount.items(), key=operator.itemgetter(1), reverse=True)
        
        
        for k in dictuple:                    
            s = " indice " + str(int(k[0],2)) + " aparece " + str(k[1])
            self.m_resultado.append(s)
        if self.stateSearch == self.SEARCHCANCEL:
            self.txout +="\nCANCELED SEARCH BY USER"
        else:
            self.txout +="\nEND SEARCH"        
        self.stateSearch = self.SEARCHENDED        
        #resultado.sort(reverse=True)
    
        

         
 
