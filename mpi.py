from mpi4py import MPI

INIT_MSG = 1
INFO_MSG = 2
LEAD_MSG = 3

# run with 6 processes
# mpiexec -n 6 python mpi.py
comm = MPI.COMM_WORLD
size = comm.Get_size()
rank = comm.Get_rank()

matrix = [
    [0, 1, 1, 1, 0, 0],  # node 0 can talk to 1, 2, 3
    [1, 0, 0, 0, 0, 0],  # node 1 can talk to 0
    [1, 0, 0, 0, 1, 1],  # node 2 can talk to 0, 4, 5
    [1, 0, 0, 0, 0, 0],  # node 3 can talk to 0
    [0, 0, 1, 0, 0, 0],  # node 4 can talk to 2
    [0, 0, 1, 0, 0, 0],  # node 5 can talk to 2
]

# initial maxp is set to itself
maxp = rank

neighbors = []
children = []
parent = None
leader = None
for i, j in enumerate(matrix[rank]):
    if j == 1:
        neighbors.append(i)

active = True
sentInit = False
while active:
    for neighbor in neighbors:

        if comm.iprobe(source=neighbor, tag=INIT_MSG):
            children.append(neighbor)
            # p computes the largest ID among the received IDs and its own (maxp)
            maxp = max(maxp, (comm.recv(source=neighbor, tag=INIT_MSG)))

        elif comm.iprobe(source=neighbor, tag=INFO_MSG):
            # p receives message from parent then it computes new max
            maxp = max(maxp, comm.recv(source=neighbor, tag=INFO_MSG))

            # print(f"{rank} got here with maxp = {maxp}")
            if len(children) > 0:
                for child in children:
                    # p sends message to all neighbors except parent
                    comm.isend(maxp, dest=child, tag=INFO_MSG)


        elif comm.iprobe(source=neighbor, tag=LEAD_MSG):
            leader = comm.recv(source=neighbor, tag=LEAD_MSG)
            if leader < maxp:
                print(f"Error at process {rank}")
            maxp = max(leader, maxp)
            for child in children:
                comm.isend(leader, dest=child, tag=LEAD_MSG)
            active = False

    if not sentInit:
        # each process(p) waits until it has received IDs from all neighbors except one, which becomes its parent.
        if len(children) >= (len(neighbors) - 1):
            # returns array of XOR between neighbors and children
            parent = [neighbor for neighbor in neighbors if neighbor not in children]

           # len(parent) should always be either 1 or 0
            if len(parent) > 0:
                parent = parent[0]
            else:
                # in the event process 2 somehow sends a message to process 4 before 4 sends to 2, for example.
                parent = neighbors[0]
            # p sends message to parent with maxp
            comm.isend(maxp, dest=parent, tag=INIT_MSG)
            # print(f"rank {rank} sending msg to parent {parent}")
            # p sends maxp message to all neighbors except parent
            for child in children:
                comm.isend(maxp, dest=child, tag=INFO_MSG)
            # print(f"rank {rank} sending msg to children {children}")
            sentInit = True

    if len(children) == len(neighbors):
        leader = maxp
        for child in children:
            comm.isend(leader, dest=child, tag=LEAD_MSG)
        active = False

print(f"p:{rank} has terminated with neighbors:{neighbors}, children: {children}, parent: {parent}, my maxp is {maxp}, and I voted for:{leader}")

# the largest ID becomes the leader
if rank == leader:
    print(f"I am process {rank}, and I have been elected the leader.")
