#!/usr/bin/env python
#
# Shell-script style.

import os
import requests
import shutil
import subprocess
import sys
import tempfile
import time
import signal

WEBPORT = '8084'
APIKEY = 'super'

ACL_LIST_TPL = """
# Generated by runtests.py
# local host
127.0.0.1
::1
"""

wait = ('--wait' in sys.argv)
if wait:
    sys.argv.remove('--wait')

cmd1 = ("../wforce/wforce -D -C ./wforce1.conf -R ../wforce/regexes.yaml").split()
cmd2 = ("../wforce/wforce -D -C ./wforce2.conf -R ../wforce/regexes.yaml").split()
cmd4 = ("../wforce/wforce -D -C ./wforce4.conf -R ../wforce/regexes.yaml").split()
webcmd = (".venv/bin/python ./webhook_server.py").split()
udpsinkcmd = (".venv/bin/python ./udp_sink.py").split()
ta_cmd = ("../trackalert/trackalert -D -C ./trackalert.conf").split()
report_cmd = (".venv/bin/python ../report_api/runreport.py").split()

# Now run wforce and the tests.
print("Launching wforce (1 and 2 and 4)...")
print(' '.join(cmd1))
print(' '.join(cmd2))
print(' '.join(cmd4))
proc1 = subprocess.Popen(cmd1, close_fds=True)
proc2 = subprocess.Popen(cmd2, close_fds=True)
proc4 = subprocess.Popen(cmd4, close_fds=True)
webproc = subprocess.Popen(webcmd, close_fds=True)
webpid = webproc.pid
udpproc = subprocess.Popen(udpsinkcmd, close_fds=True)
udppid = udpproc.pid
taproc = subprocess.Popen(ta_cmd, close_fds=True)
tapid = taproc.pid
reportproc = subprocess.Popen(report_cmd, close_fds=True)
reportpid = reportproc.pid

def sighandler(signum, frame):
    proc1.terminate()
    proc1.wait()
    proc2.terminate()
    proc2.wait()
    proc4.terminate()
    proc4.wait()
    webproc.terminate()
    webproc.wait()
    udpproc.terminate()
    udpproc.wait()
    taproc.terminate()
    taproc.wait()
    reportproc.terminate()
    reportproc.wait()
    subprocess.call(["/bin/stty", "sane"])

signal.signal(signal.SIGINT, sighandler)

print("Waiting for webserver port to become available...")
available = False
for try_number in range(0, 10):
    try:
        res = requests.get('http://127.0.0.1:%s/' % WEBPORT)
        available = True
        break
    except:
        time.sleep(0.5)

if not available:
    print("Webserver port not reachable after 10 tries, giving up.")
    proc1.terminate()
    proc1.wait()
    proc2.terminate()
    proc2.wait()
    proc4.terminate()
    proc4.wait()
    webproc.terminate()
    webproc.wait()
    udpproc.terminate()
    udpproc.wait()
    taproc.terminate()
    taproc.wait()
    subprocess.call(["/bin/stty", "sane"])
    sys.exit(2)

print("Running tests...")
rc = 0
test_env = {}
test_env.update(os.environ)
test_env.update({'WEBPORT': WEBPORT, 'APIKEY': APIKEY, 'WEBPID': str(webpid)})

try:
    print("")
    p = subprocess.check_call(["nosetests", "--with-xunit"], env=test_env)
except subprocess.CalledProcessError as ex:
    rc = ex.returncode
finally:
    if wait:
        print("Waiting as requested, press ENTER to stop.")
        raw_input()
    proc1.terminate()
    proc1.wait()
    proc2.terminate()
    proc2.wait()
    proc4.terminate()
    proc4.wait()
    webproc.terminate()
    webproc.wait()
    udpproc.terminate()
    udpproc.wait()
    taproc.terminate()
    taproc.wait()
    reportproc.terminate()
    reportproc.wait()

subprocess.call(["/bin/stty", "sane"])
    
sys.exit(rc)
