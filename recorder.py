import pickle
import sys
import threading

from snapshot import Snapshot

class Recorder(): 
  def __init__(self, pid):
      self.pid = pid
      self.snapshots = {}
      self.sockets = [None] * 4   # Sockets for receiving snapshots
      self.mutex = threading.Lock()

  ''' Initialize socket array entry '''
  def initialize_socket(self, pid, socket):
    self.sockets[pid] = socket


  ''' Saves local state and starts recording incoming channels '''
  def create_snapshot(self, snapshot_id, pid, balance): 
    snapshot = Snapshot(*snapshot_id)
    self.snapshots[snapshot.id] = snapshot
    snapshot.update_process_state(pid, balance)
    return snapshot


  ''' Update all current snapshots with incoming message '''
  def update_channels(self, src, dest, value): 
    self.mutex.acquire()
    for id, snapshot in self.snapshots: 
      snapshot.update_channel_state(src, dest, value)
    self.mutex.release()


  ''' Stop recording channel `src` for snapshot (llc, pid) '''
  def close_channel(self, snapshot_id, src):
    snapshot = self.snapshots[snapshot_id]
    snapshot.close_channel_state(src)
    self._check_ready_state(snapshot_id)


  ''' Handles receiving local snapshot from other processes '''
  def update_snapshot(self, sock, index): 
    print(f'Update snapshot client {index}')
    self.sockets[index] = sock
    while True:
      try:
        data = pickle.loads(sock.recv(1024))
        snapshot = self.snapshots[data['id']]
        snapshot.merge_snapshot_data(data)
        self._check_ready_state(data['id'])
      except EOFError:
        print(f"Disconnected from Client {index}")
        sock.close()
        self.sockets[index] = None
        sys.exit()
      except Exception as e:
        print(e)
    sock.close()
    self.sockets[index] = None


  '''
  Checks for snapshot ready state and sends or prints 
  snapshot if ready.
  '''
  def _check_ready_state(self, snapshot_id):
    llc, pid = snapshot_id 
    snapshot = self.snapshots[snapshot_id]
    if self.pid == pid and snapshot.get_global_ready_state(): 
      snapshot.print()
      self.snapshots.remove(snapshot.id)
    elif self.pid != pid and snapshot.get_local_ready_state(): 
      socket = self.sockets[pid]
      payload = snapshot.get_snapshot_data()
      socket.sendall(pickle.dumps(payload))
      self.snapshots.remove(snapshot.id)     

  ''' Close sockets '''
  def close_sockets(self): 
    for sock in self.sockets:
      if sock is not None:
        sock.close()