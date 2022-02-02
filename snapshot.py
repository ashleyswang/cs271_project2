from concurrent.futures import process
from utility import *

class Snapshot:

  def __init__(self, llc, pid, balance): 
    self.id = (llc, pid)
    self.process_states = [None] * 4
    self.channel_states = {}
    self.open_channels = Network.incoming(pid).copy()

  def update_process_state(self, pid, value): 
    self.process_states[pid] = value

  def update_channel_state(self, src, dest, value): 
    if (src, dest) not in self.channel_states: 
      self.channel_states[src, dest] = []
    self.channel_states[src, dest] += [value]

  def close_channel_state(self, src): 
    self.open_channels.remove(src)

  def get_local_ready_state(self):
    return len(self.open_channels) < 1

  def get_global_ready_state(self): 
    return (None not in self.process_states and 
      self.get_local_ready_state())

  def send_formatting(self):
    pass

  # TODO: finish
  def print(self):
    pass