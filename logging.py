import time

class colors:
  RED = '\033[91m'
  YELLOW = '\033[33m'
  GREEN = '\033[32m'
  BLUE = '\033[34m'
  GREY = '\033[90m'
  ENDC = '\033[0m'

def log(*args, **kwargs):
  debug_print(colors.GREY, *args, colors.ENDC, **kwargs)


def info(*args, **kwargs):
  debug_print(colors.BLUE, *args, colors.ENDC, **kwargs)


def notice(*args, **kwargs):
  debug_print(colors.YELLOW, *args, colors.ENDC, **kwargs)


def success(*args, **kwargs):
  debug_print(colors.GREEN, *args, colors.ENDC, **kwargs)


def fail(*args, **kwargs):
  debug_print(colors.RED, *args, colors.ENDC, **kwargs)


def debug_print(color=colors.ENDC, *args, **kwargs):
  timestamp = time.strftime("%H:%M:%S", time.localtime())
  print(f"{color}{timestamp}   ", *args, **kwargs)


if __name__ == "__main__":
  for i in range(100):
    print(f'\033[{i}m {i} \033[0m')