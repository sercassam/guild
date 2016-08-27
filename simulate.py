import os
import threading
import Queue

from character import Character
from subprocess import call

SIMC_PATH = '../simc/engine/simc'
TMP_SIMS_PATH = './.tmp_sims/'
TMP_SIMS_FILE = 'tmp.tmpsim'


def _GetArmoryString(t):
  return 'armory={},{},{}'.format(t.locale, t.realm, t.name)


def RunSimCOnToon(toon, out_filepath):
  outfile = open(out_filepath, 'w+')
  fnull = open(os.devnull, "w")
  call([SIMC_PATH, _GetArmoryString(toon)], stdout=outfile, stderr=fnull)


def ParseAllDPSFromFile(filename):
  with open(filename, 'r') as f:
    lines = f.readlines()
    dps_map = {}
    found_dps = False
    for line in lines:
      if line.startswith("DPS Ranking:"):
        found_dps = True
      elif found_dps:
        stripped_line = line.strip()

        # Next whitespace means end of DPS section
        if not stripped_line:
          break

        split_line = stripped_line.split()
        dps = split_line[0]
        name = split_line[2]

        if name.lower() != 'raid':
          dps_map[name.lower()] = int(dps)

    return dps_map


def _SimulateAndParseDPS(toon, result_queue):
  temp_filepath = os.path.join(TMP_SIMS_PATH, toon.name)
  RunSimCOnToon(toon, temp_filepath)
  all_dps = ParseAllDPSFromFile(temp_filepath)

  for name in all_dps:
    result_queue.put((name, all_dps[name]))


if __name__ == '__main__':
  members = ['tiryas', 'tiryas', 'tiryas', 'tiryas', 'tiryas', ]
  toons = map(Character, members)

  if not os.path.exists(TMP_SIMS_PATH):
    os.makedirs(TMP_SIMS_PATH)

  # Multithread simcraft for each toon. The part that takes the longest is
  # probably the wowarmory api call, so we could just only multithread that.
  dps_queue = Queue.Queue()
  threads = []
  for toon in toons:
    t = threading.Thread(target=_SimulateAndParseDPS, args=(toon,dps_queue))
    threads.append(t)
    t.start()

  for t in threads:
    t.join()

  while not dps_queue.empty():
    print dps_queue.get()
