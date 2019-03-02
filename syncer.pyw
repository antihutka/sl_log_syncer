import sys
sys.stdout = open("stdout.txt", "a")
sys.stderr = open("stderr.txt", "a")
print("--new run--")
print("--new run--", file=sys.stderr)
import syncer
