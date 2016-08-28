import os
import threading
import Queue

import numerical_util

from character import Character
from functools import partial
from subprocess import call
from multiprocessing import Pool

SIMC_PATH = '../simc/engine/simc'
TMP_SIMS_PATH = './.tmp_sims/'
TMP_SIMS_FILE = 'tmp.tmpsim'
TMP_ARMORY_PATH = '.armory'


def _GetArmoryString(t):
  return 'armory={},{},{}'.format(t.locale, t.realm, t.name)


def RunSimCOnToon(toon, out_filepath):
  outfile = open(out_filepath, 'w+')
  fnull = open(os.devnull, "w")

  toon_armory_path = os.path.join(TMP_ARMORY_PATH, toon.ArmoryFileName())
  if os.path.isfile(toon_armory_path):
    command = [SIMC_PATH, toon_armory_path]
  else:
    command = [SIMC_PATH, _GetArmoryString(toon)]

  if toon.talents is not None:
    command.append("talents={}".format(toon.talents))

  print command
  call(command, stdout=outfile, stderr=fnull)


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
          dps_map[filename] = int(dps)

    return dps_map


def _SimulateAndParseDPS(toon):
  temp_filepath = os.path.join(TMP_SIMS_PATH, toon.DebugString())
  RunSimCOnToon(toon, temp_filepath)
  all_dps = ParseAllDPSFromFile(temp_filepath)

  return all_dps.popitem() if len(all_dps) > 0 else None


def _GenerateAllTalentPermutations():
  return numerical_util.GenerateAllDigitPermutations(3, 7)


def _ParseTalentsFromProfile(filename):
  if not os.path.isfile(filename):
    return

  with open(filename, 'r') as f:
    for line in f.readlines():
      if line.strip().startswith('talents='):
        talents = line.strip()[-7:]
        std_talents = []

        for i in xrange(len(talents)):
          std_talents.append(str(int(talents[i]) + 1))

        return ''.join(std_talents)


def _FetchToonFromArmory(toon):
  armory_path = os.path.join(TMP_ARMORY_PATH, toon.ArmoryFileName())
  command = [SIMC_PATH, _GetArmoryString(toon), "save={}".format(armory_path)]

  fnull = open(os.devnull, "w")
  call(command, stdout=fnull, stderr=fnull)

  toon.talents = _ParseTalentsFromProfile(armory_path)


def _FetchToonsFromArmory(toons):
  if not os.path.exists(TMP_ARMORY_PATH):
    os.mkdir(TMP_ARMORY_PATH)

  # Multithread armory fetch.
  threads = []
  for toon in toons:
    t = threading.Thread(target=_FetchToonFromArmory, args=(toon,))
    threads.append(t)
    t.start()

  for t in threads:
    t.join()


if __name__ == '__main__':
  members = ['tiryas', 'myspeld', 'drifter', 'sengshi']
  repr_toons = map(Character, members)
  _FetchToonsFromArmory(repr_toons)

  toons = []
  for toon in repr_toons:
    if toon.talents is not None:
      talent_array = list(toon.talents)
      for t in numerical_util.GenerateKDiffPermutations(talent_array, 3, 1):
        toons.append(Character(toon.name, talents=''.join(t)))

  if not os.path.exists(TMP_SIMS_PATH):
    os.makedirs(TMP_SIMS_PATH)

  # Multithread simcraft for each toon. The part that takes the longest is
  # probably the wowarmory api call, so we could just only multithread that.
  dps_queue = Queue.Queue()
  index = 0

  tp = Pool(8)
  result = tp.map(_SimulateAndParseDPS, toons)
  for r in result:
    print r