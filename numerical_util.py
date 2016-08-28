DIGIT_SYMBOLS = ["1", "2", "3", "4", "5", "6", "7", "8", "9"]

def GenerateAllDigitPermutations(base, digits):
  perms = []
  assert 1 < base <= len(DIGIT_SYMBOLS) and digits > 0

  def _DigitToString(n):
    return DIGIT_SYMBOLS[n]

  current_number = [0] * digits
  for i in xrange(base ** digits):
    perms.append(''.join(map(_DigitToString, current_number)))

    carry = 1
    for index in xrange(digits):
      current_number[index] += 1
      if carry == 0 or current_number[index] < base:
        break

      current_number[index] = 0

  return perms

def NumDiff(a, b):
  assert len(a) == len(b)
  answer = 0
  for i in xrange(len(a)):
    if a[i] != b[i]:
      answer += 1

  return answer

# Generates all permutations that have less than or equal to k-digits different
# from the input.
def GenerateKDiffPermutations(input, base, k):
  print input, base, k
  answer = []
  for perm in GenerateAllDigitPermutations(base, len(input)):
    if NumDiff(perm, input) <= k:
      answer.append(perm)

  return answer

