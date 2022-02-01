# Mapping letters to numbers for process IDs
A = 0
B = 1 
C = 2
D = 3

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
    