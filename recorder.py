import pickle
import sys
import time
import threading

from snapshot import Snapshot
from logging import *
from utility import *

DELAY = 3

''' Keeps track of all pending snapshots for single process '''
class Recorder(): 
  def __init__(self, pid):
      self.pid = pid
      self.snapshots = {}
      self.sockets = [None] * 4   # Sockets for receiving snapshots
      self.mutex = threading.Lock()
      self.lock = threading.Lock()


  ''' Initialize socket array entry '''
  def initialize_socket(self, pid, socket):
    self.sockets[pid] = socket


  ''' Saves local state and starts recording incoming channels '''
  def create_snapshot(self, snapshot_id, pid, balance): 
    self.mutex.acquire()
    snapshot = Snapshot(snapshot_id, pid)
    self.snapshots[snapshot.id] = snapshot
    snapshot.update_process_state(pid, balance)
    self.mutex.release()
    return snapshot


  ''' Update all current snapshots with incoming message '''
  def update_channels(self, src, dest, value, marker=False): 
    self.mutex.acquire()
    for snapshot in self.snapshots.values(): 
      snapshot.update_channel_state(src, dest, value, marker)
    self.mutex.release()


  ''' Stop recording channel `src` for snapshot (llc, pid) '''
  def close_channel(self, snapshot_id, src):
    self.mutex.acquire()
    snapshot = self.snapshots[snapshot_id]
    snapshot.close_channel_state(src, self.pid)
    self._check_ready_state(snapshot_id)
    self.mutex.release()


  ''' Handles receiving local snapshot from other processes '''
  def update_snapshot(self, sock, index): 
    self.sockets[index] = sock
    while True:
      try:
        data = pickle.loads(sock.recv(1024))
        snapshot = self.snapshots[data['id']]
        self.lock.acquire()
        snapshot.merge_snapshot_data(data)
        info(f"SNAPSHOT: Received local snapshot for {snapshot.str_id} from Client {processes[index]}")
        self._check_ready_state(data['id'])
        self.lock.release()
      except EOFError:
        info(f"SNAPSHOT: Disconnected from Client {processes[index]}")
        sock.close()
        self.sockets[index] = None
        sys.exit()
      # except Exception as e:
      #   print(e)
      #   info(f"SNAPSHOT: Disconnected from Client {processes[index]}")
      finally:
        if self.lock.locked(): 
          self.lock.release()
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
      # print("global check true")
      snapshot.print()
      self.snapshots.pop(snapshot.id)
    elif self.pid != pid and snapshot.get_local_ready_state(): 
      socket = self.sockets[pid]
      payload = snapshot.get_snapshot_data()
      info(f"SNAPSHOT: Ready to send local snapshot for {snapshot.str_id}")
      time.sleep(DELAY)
      socket.sendall(pickle.dumps(payload))
      self.snapshots.pop(snapshot.id)     


  ''' Close sockets '''
  def close_sockets(self): 
    for sock in self.sockets:
      if sock is not None:
        sock.close()