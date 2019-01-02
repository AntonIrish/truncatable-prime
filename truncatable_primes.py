#!/usr/bin/env python

import math
import random

class MillerRabinPrimeChecker(object):
  # max_cumulative_error_probability is the upper bound of the probability
  # IsPrime() returns at least one Type-I error in the long run for uniformly
  # random inputs from [1, N] for sufficiently large N.  (This is not a
  # particularly strict bound.  See
  # https://en.wikipedia.org/wiki/Miller-Rabin_primality_test for details and
  # preconditions.)
  def __init__(self, max_cumulative_error_probability=1e-12):
    self._max_cumulative_error = max_cumulative_error_probability
    self._cumulative_error_sofar = 0
    self._error_opportunity_count = 0

  def IsPrime(self, n):
    if n == 2:
      return True
    if n <= 1:
      return False
    if n % 2 == 0:
      return False

    # n - 1 == 2**r * d
    d = n - 1
    r = 0
    while d % 2 == 0:
      r += 1
      d //= 2

    bases_gen, reporter = self._GetBasesGenAndReporter(n)
    result = True
    for base in bases_gen:
      if self._IsDefinitelyComposite(base, n, d, r):
        result = False
        break
    reporter(result)
    return result

  def _IsDefinitelyComposite(self, base, n, d, r):
    x = pow(base, d, n)
    if x == 1:
      return False
    for _ in range(r):
      if x == n - 1:
        return False
      x = (x * x) % n
    return True

  def _GetBasesGenAndReporter(self, n):
    if n < 3215031751:
      return {x for x in {2, 3, 5, 7} if x < n}, lambda x: None
    acceptable_error_probability_for_this_n = (
      self._max_cumulative_error - self._cumulative_error_sofar
      ) / float(max(100, self._error_opportunity_count))
    # 4 ** -k <= acceptable_error_probability_for_this_n
    k = int(math.ceil(-math.log(acceptable_error_probability_for_this_n, 4)))
    def _bases_gen():
      for _ in range(k):
        yield random.randint(1, n - 1)
    class Reporter(object):
      def __init__(self, checker):
        self._checker = checker
        self._reported = False
      def __del__(self):
        assert self._reported, "Reporter not called!"
      def Report(self, is_prime):
        if is_prime:
          self._checker._cumulative_error_sofar += acceptable_error_probability_for_this_n
          self._checker._error_opportunity_count += 1
        self._reported = True
    return _bases_gen(), Reporter(self).Report

def Doit(eight_becomes_three=False):
  IsPrime = MillerRabinPrimeChecker().IsPrime

  w2ps = {1: set([x for x in range(2, 10) if IsPrime(x)])}
  width = 0
  while True:
    width += 1
    current_prime_set = w2ps[width]
    if len(current_prime_set) == 0:
      break
    print("%d truncatable primes with %d digits: %s" % (
      len(current_prime_set),
      width,
      (", ".join([str(x) for x in sorted(current_prime_set)])
       if len(current_prime_set) < 10
       else ", ".join([str(x) for x in sorted(current_prime_set)[:10]]) + ", ...")))
    next_prime_set = set()
    for p in current_prime_set:
      for nd in range(1, 10):
        cand = int(str(nd) + str(p))
        if not eight_becomes_three:
          okay = IsPrime(cand)
        else:
          okay = (IsPrime(cand) and
                  (nd != 8 or
                   IsPrime(int(str(3) + str(p)))))
        if okay:
          next_prime_set.add(cand)
    w2ps[width + 1] = next_prime_set

def Main():
  print("Truncatbale primes (https://community.wolfram.com/groups/-/m/t/1569707)\n")
  Doit()
  print("\nWhat if 8 truncates to 3? (cf. https://bit.ly/2LJF4Lk)\n")
  Doit(eight_becomes_three=True)

if __name__ == "__main__":
  Main()
