from winsound import SND_ASYNC
from snapshot import Snapshot

class Recorder(): 
  def __init__(self, pid):
      self.pid = pid
      self.snapshots = {}
      self.sockets = [None] * 4   # Sockets for receiving snapshots

  '''
  Saves local state and starts recording incoming channels
  '''
  def create_snapshot(self, id, pid, balance): 
    snapshot = Snapshot(id, balance)
    self.snapshots[snapshot.id] = snapshot
    snapshot.update_process_state(pid, balance)
    return snapshot

  ''' 
  Update all current snapshots with incoming message
  '''
  def update_channels(self, src, dest, value): 
    for id, snapshot in self.snapshots: 
      snapshot.update_channel_state(src, dest, value)

  ''' socket thread '''
  def update_snapshot(): 
    # socket.recv(1024)
    # unpack
    # check for llc & pid
    # update snapshot
    # check ready_send

  def close_channel(self, llc, pid, src):
    snapshot = self.snapshots[llc, pid]
    snapshot.close_channel_state(src)
    self._check_ready_send(llc, pid)

  def _check_ready_send(self, llc, pid): 
    snapshot = self.snapshots[llc, pid]
    # Snapshot is requested by process
    if self.pid == pid and snapshot.get_global_ready_state(): 
      snapshot.print()
      self.snapshots.remove(snapshot.id)
    elif self.pid != pid and snapshot.get_local_ready_state(): 
      sock = self.sockets[pid]
      sock.send(snapshot.send_formatting())
      self.snapshots.remove(snapshot.id)     

