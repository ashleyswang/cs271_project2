from concurrent.futures import process
from utility import *

class Snapshot:

  def __init__(self, snapshot_id, host_id): 
    self.id = snapshot_id
    self.process_states = [None] * 4
    self.channel_states = {}
    self.open_channels = Network.incoming(host_id).copy()

  def update_process_state(self, pid, value): 
    self.process_states[pid] = value

  def update_channel_state(self, src, dest, value): 
    if (src, dest) not in self.channel_states: 
      self.channel_states[src, dest] = []
    self.channel_states[src, dest] += [value]

  def close_channel_state(self, src): 
    print(self.open_channels, src)
    self.open_channels.remove(src)

  def get_local_ready_state(self):
    return len(self.open_channels) < 1

  def get_global_ready_state(self): 
    return (None not in self.process_states and 
      self.get_local_ready_state())

  def get_snapshot_data(self):
    return {
      "op" : "MARKER",
      "id" : self.id,
      "pr_state" : self.process_states,
      "ch_state" : self.channel_states
    }

  def merge_snapshot_data(self, data):
    if (data["id"] != self.id):
      print("not the same id, no update")
      return

    # Merge Process & Channel States
    pstate = data["pr_state"]
    self.process_states = [pstate[i] if pstate[i] != None 
      else self.process_states[i] for i in range(4)]
    self.channel_states = data["ch_state"] | self.channel_states

  # TODO: finish
  def print(self):
    print(self.process_states)
    print(self.channel_states)