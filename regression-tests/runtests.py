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

cmd1 = ("../wforce -C ./wforce1.conf").split()
cmd2 = ("../wforce -C ./wforce2.conf").split()

# Now run wforce and the tests.
print "Launching wforce (1 and 2)..."
print ' '.join(cmd1)
print ' '.join(cmd2)
proc1 = subprocess.Popen(cmd1, close_fds=True)
proc2 = subprocess.Popen(cmd2, close_fds=True)

print "Waiting for webserver port to become available..."
available = False
for try_number in range(0, 10):
    try:
        res = requests.get('http://127.0.0.1:%s/' % WEBPORT)
        available = True
        break
    except:
        time.sleep(0.5)

if not available:
    print "Webserver port not reachable after 10 tries, giving up."
    proc1.terminate()
    proc1.wait()
    proc2.terminate()
    proc2.wait()
    sys.exit(2)

print "Running tests..."
rc = 0
test_env = {}
test_env.update(os.environ)
test_env.update({'WEBPORT': WEBPORT, 'APIKEY': APIKEY})

try:
    print ""
    p = subprocess.check_call(["nosetests", "--with-xunit"], env=test_env)
except subprocess.CalledProcessError as ex:
    rc = ex.returncode
finally:
    if wait:
        print "Waiting as requested, press ENTER to stop."
        raw_input()
    proc1.terminate()
    proc1.wait()
    proc2.terminate()
    proc2.wait()

subprocess.call(["/bin/stty", "sane"])
    
sys.exit(rc)
