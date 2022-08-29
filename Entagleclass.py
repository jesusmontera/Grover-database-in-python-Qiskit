import numpy as np
from qiskit.quantum_info import  Statevector
from qiskit.quantum_info import partial_trace
from qiskit import QuantumCircuit


class EntagleClass:            
    def __init__(self,nq):        
        self.nq=nq
        self.entgArr = np.zeros([nq, nq])
        self.entgXlist=  np.full((nq, nq), ' ', dtype='U1')
        self.puritys= np.zeros(nq)      
    #looks for cx instructions
    def __AreCXentagled(self, qc, datapos, a, b):        
        bEnta = False
        for i in range(datapos+1):            
            tupi=qc.data[i]            
            if tupi[0].name=='cx':
                isa=False
                isb=False
                for k in range(len(tupi[1])):
                    q = tupi[1][k].index
                    if q==a: isa=True
                    elif q==b: isb=True
                if isa and isb:
                    bEnta = not bEnta
        return bEnta
    # this function calcs entagled by purity and dictionary
    def calcSVentagle(self,sv):
        self.entgArr= np.zeros([self.nq, self.nq])
        self.entgXlist=  np.full((self.nq, self.nq), ' ', dtype='U1')
        self.__CalcPuritysFromSV (sv)
        dic = sv.probabilities_dict()        
        for a in range(self.nq):
            if (self.puritys[a]<1.0):
                for b in range(self.nq):
                    if a is not b and self.puritys[b]<1.0:                                                        
                        self.entgArr[a][b] = self.__CalcEntagleDic(dic,a,b,True)                            
                        # if there are cx and purity is less than one qubits must be entagled negative(10 01)
                        if self.entgArr[a][b]==0:
                            self.entgArr[a][b] = self.__CalcEntagleDic(dic,a,b,False)
                            self.entgXlist[a][b]='X'
                        elif self.entgArr[a][b]<0.49999:
                            self.entgArr[a][b] = 1.0 - self.entgArr[a][b]
                            self.entgXlist[a][b]='X'


     # this function only works in the circuit does itnt made with ccx or mct
    # no matter if the circuit was decomposed before in cx gates
    def calc_QC_SVentagle(self,qc,datapos,sv):
        
        self.entgArr= np.zeros([self.nq, self.nq])
        self.entgXlist=  np.full((self.nq, self.nq), ' ', dtype='U1')
        self.__CalcPuritysFromSV (sv)
        dic = sv.probabilities_dict()
        
        for a in range(self.nq):
            if (self.puritys[a]<1.0):
                for b in range(self.nq):
                    if a is not b and self.puritys[b]<1.0:
                        if self.__AreCXentagled(qc,datapos,a,b):
                                
                            self.entgArr[a][b] = self.__CalcEntagleDic(dic,a,b,True)                            
                            # if there are cx and purity is less than one qubits must be entagled negative(10 01)
                            if self.entgArr[a][b]==0:
                                self.entgArr[a][b] = self.__CalcEntagleDic(dic,a,b,False)
                                self.entgXlist[a][b]='X'
                            elif self.entgArr[a][b]<0.49999:
                                self.entgArr[a][b] = 1.0 - self.entgArr[a][b]
                                self.entgXlist[a][b]='X'
                                
    
    def __CalcEntagleDic(self, dic,iqa,iqb, bEntagleEqual=True):        
        enta=0
        for key, value in dic.items(): 
            #print(key, ' : ', value)                
            if key[(self.nq-1)-iqa]==key[(self.nq-1)-iqb]:
                enta +=value
        if not bEntagleEqual: enta = 1.0 - enta
        return enta

    def __GetQubitEntagle(self,a):
        e=0.
        n=0
        for b in range(self.nq):
            if a is not b and np.round(self.entgArr[a][b],5) > 0.:                
                e += self.entgArr[a][b]
                n += 1
        if n >1 : e /= n
        return e
    def GetQubitsEntagle(self,a,b):
        return self.entgArr[a][b]
    def __CalcPuritysFromSV(self,sv):        
        scons="pureza de purity: \n" 
        for i in range(self.nq):            
            self.puritys[i] = np.round(abs(partial_trace(sv,[i]).purity()),5)                         
    def PurityMedia(self):
        m=0
        for a in range(self.nq):
            m += self.puritys[a]
        return np.round(m / self.nq,5)
    def GetEntagleString(self, bDetail=False):
        s= "entagle by statevector.probabilities_dict + purity \n"
        na=0
        for a in range(self.nq):
            ea = np.round(self.__GetQubitEntagle(a),5)
            if ea == 0 : continue
            na+=1
            s += 'Q' + str(a) + " = " + str(ea) + "  purity = " + str(self.puritys[a])
            if bDetail:
                s+=" detail [ "
                for b in range(self.nq):
                    if b is not a and self.entgArr[a][b] > 0.:
                        s += 'Q' + str(b) + str(self.entgXlist[a][b]) + " =" +  str(np.round(self.entgArr[a][b],3)) + " "
                s +=" ]"
            s += "\n"
        if na==0: s +="qubits NOT entagled ( purity media= " + str(self.PurityMedia()) + " )"
                
        return s + "\n"
            
                        
    
