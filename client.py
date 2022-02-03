import os
import pickle
import socket
import sys
import threading
import time

from connect import *
from utility import *
from process import Process

DELAY = 3

def do_exit():
  PROC.close()
  cserver.close()
  iserver.close()
  os._exit(0)


def handle_input():
  while True:
    try:
      data = input().split()
      if data[0] == "exit" or data[0] == "quit":
        do_exit()
      elif data[0] == "connect":
        connect_outgoing(PROC)
      else:
        print("Invalid command. Valid inputs are 'balance', 'transfer', or 'exit/quit'.")
    except Exception: 
      print("Invalid command. Valid inputs are 'balance', 'transfer', or 'exit/quit'.")



if __name__ == "__main__":
  if len(sys.argv) != 2:
    print(f'Usage: python {sys.argv[0]} <processId>')
    sys.exit()

  PID = processes[sys.argv[1]]
  PROC = Process(PID)
 
  # Connect to Client & Server Machines
  cserver = connect_channels(PROC)
  iserver = connect_incoming(PROC)  

  # Handle User Input
  handle_input()
  do_exit()
