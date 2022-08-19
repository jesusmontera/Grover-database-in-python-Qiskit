# Grover-database-in-python 3.6-Qiskit ( lubuntu 18.04)

Source code for searching a QRAM database value->index with Grover in Qiskit with entanglement measure

WARNING  number of qubits must we ODD because there is an auxilary qubit.

There are 2 files, qtGroverclass.py does do grover qiskit job and qtgrover.py shows the result in a graphical window.The grahical window searchs with QThread.

It can show the entaglement between qubits in each step of the search process (with the option checked do not use moe than 9 qubits).

Also shows the qubits bloch sphere so you can understand how the it works for multiple searched values. I mean if you search 2 values witch that are entagled with indexs (results) 1 (01) and 3 (11) you will se that the first bloch vector points to 1 in near 65% because both result bits are one each result , and the second vector is 50% cero and 50% one, because  it must satisfy ambiguos scond bit results 0 and 1.

Also I have code in MFC Vc6++ for windows with my own quantum engine that does the same (and faster), so no need to install Qiskit

![Alt text](ima.png?raw=true "Grover search qiskit python 3.6 pyqt5 gui")
