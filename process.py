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

  def send_markers(self, llc, pid):
    for sock in self.outgoing: 
      if sock is not None: 
        sock.sendall("MARKER", snapshot)
  
  def initiate_snapshot(self): 
    # Check for threading, MUTEX
    snapshot = self.recorder.create_snapshot(self.llc, self.pid)
    self.send_markers(snapshot.id)

  def handle_incoming(self, sock, index): 
    data = sock.recv(1024)
    # unpack
    if data == "MARKER":
      llc, pid = data[0]  # get llc and pid from data this is not actually the index though
      #second marker
      if (llc, pid) in self.recorder.snapshots: 
        self.recorder.close_channel(llc, pid, index)
      else:
        self.recorder.create_snapshot(llc, pid, self.balance)
        self.recorder.close_channel(llc, pid, index)
        self.send_markers(llc, pid)
    else: 
      value = 0
      self.recorder.update_channels(index, self.pid, value)
      self.handle_transaction(value)

  def handle_transaction(self, value):
    self.balance += value

