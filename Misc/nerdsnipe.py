'''
I got nerdsniped today. 
The integers in the file remainders.txt are the result of a mod operation p on an integer x
for successive large powers (k, k+1, etc.) P is a 3 digit prime number.
What is the value for x and p.

The annoying this is that the problem says it can be solved by pen and paper. i just dont know how
'''

from tqdm import tqdm
from math import ceil, sqrt

with open('primes.txt', 'r') as file:
    lines = [int(line.strip()) for line in file.readlines()]

def is_prime(n):
    if n <= 1:
        return False
    if n <= 3:
        return True
    if n % 2 == 0 or n % 3 == 0:
        return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0:
            return False
        i += 6
    return True

def get_primes_between(start, end):
    primes = []
    for num in range(start, end + 1):
        if is_prime(num):
            primes.append(num)
    return primes

prime_numbers = get_primes_between(853, 1000)

#github.com/0xTowel
def bsgs(g, h, p):
    N = ceil(sqrt(p - 1)) 
    tbl = {pow(g, i, p): i for i in range(N)}
    c = pow(g, N * (p - 2), p)

    # Search for an equivalence in the table. Giant step.
    for j in range(N):
        y = (h * pow(c, j, p)) % p
        if y in tbl:
            return j * N + tbl[y]

    return None

for integer in tqdm(range(1, 1000)):
    for prime in prime_numbers:
        for i in range(len(lines)):
            target = bsgs(integer, lines[i], prime)
            cycle = []
            k=0
            if target is not None:
                for i in range(12):
                    cycle.append(integer**(target+i) % prime)
                    if cycle==lines:
                        print(integer, target, prime)
                        break

# check = []
# for i in range(len(lines)):    
#     check.append(209**(25+i) % 919)
# check