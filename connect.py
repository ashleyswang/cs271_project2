import pickle
import socket
import threading

from utility import *
from logging import *

''' Connect channels for relaying finished snapshot '''
def connect_channels(proc):
  # Listener thread
  def listen(server, proc): 
    server.listen(32)
    while True: 
      sock, addr = server.accept()
      pid = pickle.loads(sock.recv(1024))
      info(f"SNAPSHOT: Connected to Client {processes[pid]}")
      threading.Thread(target=proc.recorder.update_snapshot, 
                       args=(sock, pid)).start()

  # Connect to listener of other clients
  def connect(pid, proc):
    try:
      sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      sock.connect((socket.gethostname(), 5000+pid))
      sock.sendall(pickle.dumps(proc.pid))
      info(f"SNAPSHOT: Connected to Client {processes[pid]}")
      threading.Thread(target=proc.recorder.update_snapshot, 
                       args=(sock, pid)).start()
    except ConnectionRefusedError:
      fail(f"SNAPSHOT: Failed Connection to Client {processes[pid]}.")

  # Connection protocol
  server = socket.socket()
  server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
  server.bind((socket.gethostname(), 5000 + proc.pid))
  threading.Thread(target=listen, args=(server, proc)).start()

  for i in range(proc.pid):
    connect(i, proc)
  return server


''' Listen for incoming requests to process '''
def connect_incoming(proc):
  # Listener thread
  def listen(server, proc): 
    server.listen(32)
    while True: 
      sock, addr = server.accept()
      pid = pickle.loads(sock.recv(1024))
      success(f"Connected to Incoming Client {processes[pid]}")
      threading.Thread(target=proc.handle_incoming, 
                       args=(sock, pid)).start()

  # Connection Protocol
  server = socket.socket()
  server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
  server.bind((socket.gethostname(), 8000 + proc.pid))
  info("Listening for Incoming Client Connections...")
  threading.Thread(target=listen, args=(server, proc)).start()
  return server


''' Connect to outgoing channels for process '''
def connect_outgoing(proc):
  # Connect to listener
  def connect(pid, proc):
    try:
      sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      sock.connect((socket.gethostname(), 8000+pid))
      sock.sendall(pickle.dumps(proc.pid))
      success(f"Connected to Outgoing Client {processes[pid]}")
      proc.handle_outgoing(sock, pid)
    except ConnectionRefusedError:
      fail(f"Failed Connection to Outgoing Client {processes[pid]}")

  for i in Network.outgoing(proc.pid):
    connect(i, proc)