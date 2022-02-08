import os
import pickle
import socket
import sys
import threading
import time

from connect import *
from logging import *
from utility import *
from process import Process

DELAY = 3

def do_exit():
  PROC.close()
  iserver.close()
  cserver.close()
  os._exit(0)


def handle_input():
  while True:
    try:
      data = input().split()
      if data[0] == "exit" or data[0] == "quit":
        do_exit()
      elif data[0] == "connect":
        connect_outgoing(PROC)
      elif data[0] == "snapshot":
        print('Initiating Global Snapshot Protocol...')
        PROC.initiate_snapshot()
      elif data[0] == "balance":
        get_balance()
      elif data[0] == "transfer":
        try: 
          amount = round(float(data[1].strip('$')), 2)
          recipient = processes[data[2]]
          do_transfer(recipient, amount)
        except ValueError:
          print("Invalid argument types. Please input a integer PID and float amount.")
      elif data[0] == "marker":
        recipient, llc, pid = int(data[1]), int(data[2]), int(data[3])
        payload = { 'op' : 'MARKER', 'id' : (llc, pid) }
        sock = PROC.outgoing[recipient]
        sock.sendall(pickle.dumps(payload))
      else:
        print("Invalid command. Valid inputs are 'connect', 'snapshot', 'balance', 'transfer', or 'exit/quit'.")
    except Exception as e: 
      print("Invalid command. Valid inputs are 'connect', 'snapshot', 'balance', 'transfer', or 'exit/quit'.")

def get_balance():
  print(f"Balance: ${PROC.balance:.2f}", flush=True)

def do_transfer(pid, value):
  PROC.do_transfer(pid, value)

if __name__ == "__main__":
  if len(sys.argv) != 2:
    print(f'Usage: python {sys.argv[0]} <processId>')
    sys.exit()

  PID = processes[sys.argv[1]]
  PROC = Process(PID)
 
  # Connect to Client & Server Machines
  iserver = connect_incoming(PROC)  
  cserver = connect_channels(PROC)

  # Handle User Input
  handle_input()
  do_exit()
