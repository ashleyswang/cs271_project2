import threading

from logging import *
from utility import *


''' Object representing a snapshot for a single request'''
class Snapshot:
  def __init__(self, snapshot_id, host_id): 
    self.id = snapshot_id
    self.str_id = f"({snapshot_id[0]}, {processes[snapshot_id[1]]})"
    self.process_states = [None] * 4
    self.channel_states = {}
    self.open_channels = Network.incoming(host_id).copy()
    self.lock = threading.Lock()


  ''' Updates process state with current balance '''
  def update_process_state(self, pid, value): 
    self.process_states[pid] = value


  ''' Updates channel state with incoming messages '''
  def update_channel_state(self, src, dest, value, marker=False): 
    if (src, dest) not in self.channel_states: 
      self.channel_states[src, dest] = []
    if marker and value['id'] == self.id:
      return
    if src in self.open_channels:
      self.channel_states[src, dest] += [value]


  ''' Stops recording messages for channel'''
  def close_channel_state(self, src, dest): 
    if (src, dest) not in self.channel_states: 
      self.channel_states[src, dest] = []
    self.open_channels.remove(src)


  ''' Returns true if snapshot is ready to sent to requester '''
  def get_local_ready_state(self):
    return len(self.open_channels) < 1


  ''' Returns true if snapshot is ready to print '''
  def get_global_ready_state(self): 
    # print(self.process_states)
    # print(self.get_local_ready_state())
    return (None not in self.process_states and 
      self.get_local_ready_state())


  ''' Returns sendable snapshot data '''
  def get_snapshot_data(self):
    return {
      "op" : "MARKER",
      "id" : self.id,
      "pr_state" : self.process_states,
      "ch_state" : self.channel_states
    }


  ''' Merges local snapshot data from other process '''
  def merge_snapshot_data(self, data):
    if (data["id"] != self.id):
      fail("not the same id, no update")
      return
    # Merge Process & Channel States
    self.lock.acquire()
    pstate = data["pr_state"]
    self.process_states = [pstate[i] if pstate[i] != None 
      else self.process_states[i] for i in range(4)]
    self.channel_states = data["ch_state"] | self.channel_states
    self.lock.release()


  ''' Prints formatted string for snapshot'''
  def print(self):
    title = f"----- SNAPSHOT {self.str_id} -----"
    print(title)
    print(f"Local States:\
      \n\tA: ${self.process_states[A]}\
      \n\tB: ${self.process_states[B]}\
      \n\tC: ${self.process_states[C]}\
      \n\tD: ${self.process_states[D]}\n"
      )
    print("Channel States")
    keys = list(self.channel_states.keys())
    keys.sort()
    for src, dest in keys:
      print(f"\t{processes[src]} -> {processes[dest]}: {self.channel_states[src, dest]}")
    print("-"*len(title))