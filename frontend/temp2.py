import string, random

pwd = ''.join(
                random.SystemRandom().choice(string.digits) for _ in
                range(4))

print(pwd)