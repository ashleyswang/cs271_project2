import pickle
import sys
import threading

from recorder import Recorder

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
    snapshot = self.recorder.create_snapshot(self.llc, self.pid)
    self._send_markers(snapshot.id)


  ''' Transfers $value to process dest if enough balance '''
  def do_transfer(self, dest, value): 
    if self.balance < value: return False
    socket = self.outgoing[dest]
    payload = { 'op' : 'TRANSFER', 'value' : value }
    self._update_balance(-value)
    socket.sendall(pickle.dumps(payload))
    return True
    

  ''' Thread for handling messages on incoming sockets '''
  def handle_incoming(self, sock, index): 
    self.incoming[index] = sock
    while True:
      try:
        data = pickle.loads(sock.recv(1024))
        self._update_balance()
        if data['op'] == 'MARKER':
          id = data['id'] 
          if id in self.recorder.snapshots: 
            self.recorder.close_channel(id, index)
          else:
            self.recorder.create_snapshot(id, self.pid, self.balance)
            self.recorder.close_channel(id, index)
            self._send_markers(id)
        elif data['op'] == "TRANSFER": 
          value = data['value']
          self._update_balance(value)
          self.recorder.update_channels(index, self.pid, value)
      except EOFError:
        print(f"Disconnected from Client {index}")
        sock.close()
        self.incoming[index] = None
        sys.exit()
      except Exception as e:
        print(e)
    sock.close()
    self.incoming[index] = None


  ''' Sends markers to all outgoing connections'''
  def _send_markers(self, snapshot_id):
    payload = { 'op' : 'MARKER', 'id' : snapshot_id }
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
    print(f"LLC: {(self.llc, self.pid)}")
    self.mutex.release()
