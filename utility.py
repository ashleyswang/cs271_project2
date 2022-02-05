# Mapping letters to numbers for process IDs
A, B, C, D = 0, 1, 2, 3

processes = {
  'A' : A,  'B' : B, 'C' : C,  'D' : D, 
   1 : 'A',  2 : 'B',  3: 'C',   4: 'D'
}


# Network Connections
class Network: 
  incoming_network = {
    A: [B, D],
    B: [A, C, D],
    C: [D],
    D: [B] 
  }
  outgoing_network = {
    A: [B], 
    B: [A, D], 
    C: [B], 
    D: [A, B, C]
  }

  def incoming(pid): 
    return Network.incoming_network[pid]

  def outgoing(pid):
    return Network.outgoing_network[pid]
    