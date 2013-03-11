#! -*- encoding:utf-8 -*-
import getopt
import time
import sys
from onethread import Request
from report import RuntimeReporter

__author__ = 'tangcl'

from manager import LoadManager
def start(num_agents, time_limit, url):
    runtime_stats = {-1:{"serversoftware":"", "documentlength":"",
                     "RequestsPerSecond":"", "TimePerSocond":"", "TransferRate":""}}

    lm = LoadManager(num_agents, runtime_stats)
    req = Request()
    req.url = url
    lm.add_req(req)
    start_time = time.time()

    lm.setDaemon(True)
    lm.start()

    reporter = RuntimeReporter( runtime_stats)
    elapsed_secs = 0
    while time.time() < (start_time + time_limit):
        refresh_rate = 0.5
        time.sleep(refresh_rate)

        if lm.agents_started:
            elapsed_secs = time.time() - start_time
    reporter.refresh(elapsed_secs, refresh_rate)
    lm.stop()
    print 'Done.'

def usage( msg = ''):
    """print usage info"""
    sys.stderr.write("%s: %s\n" % (sys.argv[0], msg))
    msg.stderr.write("Try 'python %s -h' for more information.\n" % sys.argv[0])

def main():
    """main docstring"""
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'c:n:t:h:u:')
    except Exception, e:
        usage(str(e))
        return 2
    frequence, timelimit, url = 0,0,""
    for k, v in opts:
        if k == '-c':
            all_num = int(v)
        elif k == "-n":
            #表示线程数,100,表示100个线程,线程中
            frequence = int(v)
            print "current frequence:", frequence
        elif k == '-t':
            timelimit = int(v)
        elif k == '-u':
            url = v
            print "request url:", url
        elif k == '-h':
            print __doc__
            return 0
    start(frequence, timelimit, url)

if __name__ == "__main__":
    main()