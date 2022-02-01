from recorder import Recorder
from snapshot import Snapshot
from utility import *

class Process:

  def __init__(self, pid):
    self.pid = pid
    self.llc = 0

    self.balance = 10  
    self.outgoing = [None] * 4
    self.incoming = [None] * 4
    self.recorder = {}

  def create_snapshot(self, llc=None, pid=None): 
    if llc is None: llc = self.llc
    if pid is None: pid = self.pid
    snapshot = Snapshot(llc, pid, self.balance)
    self.states[snapshot.id] = snapshot
    return snapshot

  def send_markers(self, snapshot):
    for sock in self.outgoing: 
      if sock is not None: 
        sock.sendall("MARKER", snapshot)
  
  def initiate_snapshot(self): 
    snapshot = self.create_snapshot()
    self.send_markers(snapshot)

    # Wait for snapshot to complete
    # print it out

  def handle_incoming(self, sock, index): 
    data = sock.recv(1024)
    if data == "MARKER":
      llc, pid = data[0]  # get llc and pid from data this is not actually the index though
      #second marker
      if (llc, pid) in states.keys(): 
        stop recording, save states of sockets
      else: 
        snapshot = self.create_snapshot(llc, pid)
        snapshot.channel_state[index, self.pid] = []
        self.send_markers(snapshot)
    else : 
      self.handle_transaction()

  def handle_transaction(self)

