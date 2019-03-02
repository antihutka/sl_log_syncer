import sys
import os
import os.path
import pymysql
import re
import datetime
import time
from configparser import ConfigParser

bad_files = ["plugin_cookies.txt", "teleport_history.txt", "typed_locations.txt", "search_history.txt"]

sys.stdout.reconfigure(encoding='utf-8')

Cfg = ConfigParser()
Cfg.read(sys.argv[1])

dbcon = pymysql.connect(
  host=Cfg.get("database", "host"),
  user=Cfg.get("database", "user"),
  password=Cfg.get("database", "pass"),
  db=Cfg.get("database", "db"),
  charset="utf8mb4")
dbcur = dbcon.cursor()
dbcur.execute("set session sql_mode='STRICT_TRANS_TABLES'")

def get_log_pos(logdir_name, log_name):
  dbcur.execute("SELECT bytepos_end FROM chat WHERE log_dir=%s AND log_name=%s ORDER BY id DESC LIMIT 1", (logdir_name, log_name));
  if dbcur.rowcount > 0:
    return dbcur.fetchone()[0]
  else:
    return 0

def extract_timestamp_and_name(logline):
  #print(logline)
  m = re.match(r"\[(20\d\d/\d\d/\d\d \d\d:\d\d)\]  (.*)", logline)
  if m:
    timestamp = m.group(1)
    name_and_message = m.group(2)
    n = re.match(r"(.+?): (.*)", name_and_message)
    if n:
      name = n.group(1)
      message = n.group(2)
      return(timestamp, name, message)
    else:
      return(timestamp, None, name_and_message)
  else:
    return None

def split_name(name):
  if not name:
    return (None, None)
  m = re.match(r"(.*)\(([a-z0-9]+(?:\.[a-z]+)?)\)$", name)
  if m:
    return (m.group(2), m.group(1))
  m = re.match(r"([A-Za-z0-9]+) ([A-Za-z]+)$", name)
  if m:
    return ((m.group(1) + "." + m.group(2)).lower(), name)
  m = re.match(r"[A-Za-z0-9]+$", name)
  if m:
    return (name.lower(), name)
  return (None, name)

linebuffer = []

def output_lines(lines, left):
  if not lines:
    return
  start_time = time.time()
  dbcur.executemany("INSERT INTO chat (log_dir, log_name, bytepos_end, timestamp_raw, timestamp_parsed, user_name, display_name, type, message) VALUES "
    "(%s, %s, %s, %s, %s, %s, %s, %s, %s)", lines);
  dbcon.commit()
  elapsed_time = time.time() - start_time
  print("%s %s %d - inserting %d rows, %d bytes left, took %fs" % (lines[0][0], lines[0][1], lines[0][2], len(lines), left, elapsed_time))
#  time.sleep(1)
#  for l in lines:
#    print(l)

def parse_logline(logdir_name, log_name, endpos, logline):
  e = extract_timestamp_and_name(logline)
  if e:
    (timestamp, fullname, message) = e
    (username, displayname) = split_name(fullname)
    timestamp_parsed = datetime.datetime.strptime(timestamp, "%Y/%m/%d %H:%M")
    type = 0
    if message.startswith("whispers: "):
      type = 1
      message = message[10:]
    elif message.startswith("shouts: "):
      type = 2
      message = message[8:]
    linebuffer.append((logdir_name, log_name, endpos, timestamp, timestamp_parsed, username, displayname, type, message))
  else:
    old = linebuffer.pop()
    if logline.startswith(" "):
      logline = logline[1:]
#    else:
#      print("Continuation line doesn't start with a space at %s %s %s '%s' prevline '%s'" % (logdir_name, log_name, endpos, logline, linebuffer[-1][4]), file=sys.stderr)
    linebuffer.append((logdir_name, log_name, endpos, old[3], old[4], old[5], old[6], old[7], old[8] + "\n" + logline))

def sync_log(logdir_name, log_name, log_path):
  logpos = get_log_pos(logdir_name, log_name)
  #print("log %s position: %d" % (log,logpos))
  size = os.path.getsize(log_path)
  with open(log_path, "r", encoding="utf-8", errors="ignore") as fh:
    fh.seek(logpos)
    while True:
      logline = fh.readline()
      if not logline:
        break
      #print("in: '%s'" % logline)
      logline = logline.rstrip("\r\n")
      #print("st: '%s'" % logline)
      endpos = fh.tell()
      parse_logline(logdir_name, log_name, endpos, logline)
      if len(linebuffer) > Cfg.getint("database", "rows"):
        last = linebuffer.pop()
        output_lines(linebuffer, size - endpos)
        linebuffer.clear()
        linebuffer.append(last)
  output_lines(linebuffer, 0)
  linebuffer.clear()

logdirs = [x for x in Cfg if x.startswith("logdir ")]
for logdir in logdirs:
  logdir_name = logdir.split(" ", 1)[1]
  path = Cfg.get(logdir, "path")
  #print("current logdir: %s => %s" % (logdir_name, path))
  
  logs = [f for f in os.listdir(path) if f.endswith(".txt") and (f not in bad_files) and os.path.isfile(path + "/" + f)]
  for log in logs:
    sync_log(logdir_name, log, path + "/" + log)

