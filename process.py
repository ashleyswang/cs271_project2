import pickle
import sys
import time
import threading

from recorder import Recorder
from utility import *
from logging import *

DELAY = 3

''' Implement snapshot protocol for a single process '''
class Process:
  def __init__(self, pid):
    self.pid = pid
    self.llc = 0

    self.balance = 10  
    self.recorder = Recorder(pid)
    self.outgoing = [None] * 4
    self.incoming = [None] * 4

    self.mutex = threading.Lock()


  ''' Initiate global snapshot protocol '''
  def initiate_snapshot(self): 
    self._update_llc()
    snapshot = self.recorder.create_snapshot(
      (self.llc, self.pid), self.pid, self.balance)
    self._send_markers(snapshot.id)


  ''' Transfers $value to process dest if enough balance '''
  def do_transfer(self, dest, value): 
    self._update_llc()
    if self.balance < value: 
      print("Transfer: INSUFFICIENT BALANCE")
      return False
    socket = self.outgoing[dest]
    if socket is None: 
      print("Transfer: NOT CONNECTED TO CLIENT")
      return False
    payload = { 'op' : 'TRANSFER', 'value' : value }
    bal_before = self.balance
    self._update_balance(-value)
    time.sleep(DELAY)
    socket.sendall(pickle.dumps(payload))
    print("Transfer: SUCCESS")
    print(f"    Balance before: ${bal_before:.2f}", flush=True)
    print(f"    Balance after : ${self.balance:.2f}", flush=True)
    return True
    

  ''' Thread for handling messages on incoming sockets '''
  def handle_incoming(self, sock, index): 
    self.incoming[index] = sock
    while True:
      try:
        data = pickle.loads(sock.recv(1024))
        self._update_llc()
        if data['op'] == 'MARKER':
          id = data['id']
          log(f"Received MARKER for Snapshot ({id[0]}, {processes[id[1]]})") 
          if id in self.recorder.snapshots: 
            notice(f"Second MARKER: Closing Channel {processes[index]} -> {processes[self.pid]}")
            self.recorder.update_channels(index, self.pid, data, marker=True)
            self.recorder.close_channel(id, index)
          else:
            notice(f"First MARKER: Recording Channel {processes[index]} -> {processes[self.pid]}")
            self.recorder.create_snapshot(id, self.pid, self.balance)
            self.recorder.update_channels(index, self.pid, data, marker=True)
            self.recorder.close_channel(id, index)
            self._send_markers(id)
        elif data['op'] == "TRANSFER":
          value = data['value']
          bal_before = self.balance
          self._update_balance(value)
          self.recorder.update_channels(index, self.pid, value)
          print(f"Transfer: RECEIVED ${value:.2f} FROM CLIENT {processes[index]}")
          print(f"    Balance before: ${bal_before:.2f}", flush=True)
          print(f"    Balance after : ${self.balance:.2f}", flush=True)
      except EOFError:
        fail(f"Disconnected from Client {processes[index]}")
        sock.close()
        self.incoming[index] = None
        sys.exit()
      except Exception as e:
        print(e)
    sock.close()
    self.incoming[index] = None


  ''' Add socket to outgoing list '''
  def handle_outgoing(self, sock, index): 
    self.outgoing[index] = sock


  ''' Sends markers to all outgoing connections'''
  def _send_markers(self, snapshot_id):
    payload = { 'op' : 'MARKER', 'id' : snapshot_id }
    time.sleep(DELAY)
    for sock in self.outgoing: 
      if sock is not None: 
        sock.sendall(pickle.dumps(payload))


  ''' Updates process balance'''
  def _update_balance(self, value): 
    self.mutex.acquire()
    self.balance += value
    self.mutex.release()


  ''' Updates Lamport Logical Clock Counter '''
  def _update_llc(self, value = None):
    self.mutex.acquire()
    if (value): self.llc = max(value, self.llc) + 1
    else: self.llc += 1
    self.mutex.release()


  ''' Close all sockets '''
  def close(self):
    for sock in self.incoming + self.outgoing:
      if sock is not None:
        sock.close()
    self.recorder.close_sockets()