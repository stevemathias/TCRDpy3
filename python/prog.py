#!/usr/bin/env python3

import time, sys

def update_progress(progress):
  '''
  Displays/Updates a progress bar in a console.
  - The input should be a float between 0 and 1
  - An input value < 0 represents a 'halt'.
  - An value value >= 1 represents 100%
  '''
  barLength = 50 # Width of the progress bar
  status = ""
  if isinstance(progress, int):
    progress = float(progress)
  if not isinstance(progress, float):
    progress = 0
    status = "Error: input must be float.\r\n"
  if progress < 0:
    progress = 0
    status = "Aborted.\r\n"
  if progress >= 1:
    progress = 1
    status = "Done.\r\n"
  block = int(round(barLength*progress))
  pbar = "\rProgress: [{}] {}% {}".format("#"*block + "-"*(barLength-block), progress*100, status)
  sys.stdout.write(pbar)
  sys.stdout.flush()

# tests
print("t1: 'foo'")
update_progress("foo")
time.sleep(1)

print("t2: '-10'")
update_progress(-10)
time.sleep(1)

print("t3: 3")
update_progress(3)
time.sleep(1)

print("t4: 0.42")
update_progress(0.42)
time.sleep(1)

print()
print("t5: 0->1")
for i in range(101):
  time.sleep(0.1)
  update_progress(i/100.0)

print("Tests completed")
