import os
import pickle
import socket
import sys
import threading
import time

DELAY = 3

def do_exit():
  MUTEX.close()
  SOCKET.close()
  os._exit(0)


def handle_input():
  while True:
    try:
      data = input().split()
    
      if data[0] == "exit" or data[0] == "quit":
        do_exit()
      elif data[0] == "balance":
        threading.Thread(target=get_balance).start()
      elif data[0] == "transfer":
        try: 
          recipient = int(data[1])
          amount = round(float(data[2].strip('$')), 2)
          if recipient not in [1, 2, 3] or recipient == PID:
            raise NameError('InvalidPID')
          threading.Thread(target=make_transfer, args=(recipient, amount)).start()
        except ValueError:
          print("Invalid argument types. Please input a integer PID and float amount.")
        except NameError:
          print("Invalid PID recipient. Please input PID from 1-3 that is not own PID.")
      elif data[0] == "queue":
        print(MUTEX.queue)
      elif data[0] == "connect":
        try:
          MUTEX.connect(int(data[1]))
        except (IndexError, ValueError):
          connect_server()
      else:
        print("Invalid command. Valid inputs are 'balance', 'transfer', or 'exit/quit'.")
    except Exception: 
      print("Invalid command. Valid inputs are 'balance', 'transfer', or 'exit/quit'.")


def connect_client(): 
  info("Listening for Client Connections...")
  threading.Thread(target=MUTEX.listen).start()

  info("Requesting Connections to Clients...")
  for i in range(1, PID):
    MUTEX.connect(i)
  

def connect_server(port=8000):
  try:
    SOCKET.connect((socket.gethostname(), port))
    SOCKET.sendall(pickle.dumps(PID))
    balance = pickle.loads(SOCKET.recv(1024))
    success(f"Connected to Blockchain Server")
    notice(f"Balance: ${balance:.2f}")
  except ConnectionRefusedError:
    fail(f"Failed to connect to server.")


def get_balance():
  MUTEX.acquire()
  print("Getting Balance...")
  MUTEX.update_llc()
  time.sleep(DELAY)
  SOCKET.sendall(pickle.dumps(("BALANCE", PID, 0, 0)))
  
  try:
    balance = pickle.loads(SOCKET.recv(1024))
    print(f"Balance: ${balance:.2f}", flush=True)
  except EOFError:
    fail("Disconnected from server.")
  MUTEX.release()


def make_transfer(recipient, amount):
  MUTEX.acquire()
  print(f"Transfering {amount} to Client {recipient}...")
  MUTEX.update_llc()
  time.sleep(DELAY)
  SOCKET.sendall(pickle.dumps(("TRANSFER", PID, recipient, amount)))
  
  try:
    status, bal_before, bal_after = pickle.loads(SOCKET.recv(1024))
    print(f"Transfer: {status}", flush=True)
    if status=="SUCCESS":
      print(f"    Balance before: ${bal_before:.2f}", flush=True)
      print(f"    Balance after : ${bal_after:.2f}", flush=True)
    else:
      print("    You don't have enough balance to make this transaction.")
      print(f"    Current Balance: {bal_before:.2f}", flush=True)
  except EOFError:
    fail("Disconnected from server.")
  MUTEX.release()


if __name__ == "__main__":
  if len(sys.argv) != 2:
    print(f'Usage: python {sys.argv[0]} <processId>')
    sys.exit()

  PID = int(sys.argv[1])
  MUTEX = LamportMutex(PID)
  SOCKET = socket.socket()
  
  notice(f"Client {PID}")

  # Connect to Client & Server Machines
  connect_client()
  connect_server()

  # Handle User Input
  handle_input()
  do_exit()
