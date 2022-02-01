class Snapshot:

  def __init__(self, llc, pid, balance): 
    self.id = (llc, pid)
    self.process_states = [None] * 4
    self.channel_states = {}

    self.update_process_state(pid, balance)

  def update_process_state(self, pid, value): 
    self.process_states[pid] = value

  def update_channel_state(self, src, dest, value): 
    if (src, dest) not in self.channel_states: 
      self.channel_states[src, dest] = []
    self.channel_states[src, dest] += [value]