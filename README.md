# mpitreeelection
program to elect leader from tree topography using mpi4py multiprocessing. Done for college multiprocessing class.

requires at least Python 3.9
execute with the following command from terminal: mpiexec -n 6 python mpi.py

This will run the program with 6 processes, which is mandatory for the program to function properly. Greater than 6 will have nodes that can't talk to anyone, and less than 6 may result in the program not terminating.
