#! -*- encoding:utf-8 -*-
import cookielib
import copy
import httplib
import random
from threading import Thread
import urllib
import urllib2
import time

'''
一个request线程请求,一直循环,知道父进程退出,跟着结束
'''
HTTP_DEBUG = True
class Request():
    def __init__(self, url='http://localhost/', method='GET', body='', headers=None, timer_group='default_timer'):
        self.url = url
        self.method = method
        self.body = body
        self.timer_group = timer_group
        if headers:
            self.headers = headers
        else:
            self.headers = {}
        self.verify = ''
        self.verify_negative = ''

        if 'user-agent' not in [header.lower() for header in self.headers]:
            self.add_header('User-Agent', 'Mozilla/4.0 (compatible; Pylot)')
        if 'connection' not in [header.lower() for header in self.headers]:
            self.add_header('Connection', 'close')
        if 'accept-encoding' not in [header.lower() for header in self.headers]:
            self.add_header('Accept-Encoding', 'identity')

    def add_header(self, header_name, value):
        self.headers[header_name] = value

class ErrorResponse():
    def __init__(self):
        self.code = 0
        self.msg = 'Connection error'
        self.headers = {}

class WhileTread(Thread):
    def __init__(self, id, runtime_stats, request_queue, results_queue):
        Thread.__init__(self)

        self.running = True
        self.id = id
        self.runtime_stats = runtime_stats  # 线程间可以直接读写进程数据段
        self.request_queue = copy.deepcopy(request_queue)
        self.results_queue = results_queue  # 线程间可以直接读写进程数据段
        self.count = 0
        self.error_count = 0
        self.default_timer = time.time

    def run(self):
        agent_start_time = time.strftime('%H:%M:%S', time.localtime())
        total_latency = 0
        total_connect_latency = 0
        total_bytes = 0
        while self.running:
            for req in self.request_queue:
                if self.running:
                    resp, content, req_start_time, req_end_time, connect_end_time = self.send(req)
                    tmp_time = time.localtime()
                    cur_date = time.strftime('%d %b %Y', tmp_time)
                    cur_time = time.strftime('%H:%M:%S', tmp_time)

                    resp_bytes = len(content)
                    latency = (req_end_time - req_start_time)
                    connect_latency = (connect_end_time - req_start_time)

                    self.count += 1
                    total_bytes += resp_bytes
                    total_latency += latency
                    total_connect_latency += connect_latency

                    self.runtime_stats[self.id] = StatCollection(resp.code, resp.msg, latency, self.count, total_latency, total_connect_latency, total_bytes)
                    self.runtime_stats[self.id].agent_start_time = agent_start_time

                    q_tuple = (self.id + 1, cur_date, cur_time, req_end_time, req.url.replace(',', ''), resp.code, resp.msg.replace(',', ''), resp_bytes, latency, connect_latency, req.timer_group)
                    self.results_queue.put(q_tuple)
                else:
                    break

    def stop(self):
        self.running = False
    def send(self, req):
        opener = urllib2.build_opener()
        if req.method.upper() == 'POST':
            request = urllib2.Request(req.url, req.body, req.headers)
        else:
            request = urllib2.Request(req.url, None, req.headers)
        req_start_time = self.default_timer()
        try:
            resp = opener.open(request)
            connect_end_time = self.default_timer()
            self.runtime_stats[-1]["serversoftware"] = resp.headers.dict["server"]
            content = resp.read()
            self.runtime_stats[-1]["documentlength"] = len(content)
        except Exception, e:  # this also catches socket errors
            connect_end_time = self.default_timer()
            resp = ErrorResponse()
            resp.code = 0
            resp.msg = str(e.reason)
            resp.headers = {}  # headers are not available in the exception
            content = ''
        req_end_time = self.default_timer()
        return resp, content, req_start_time, req_end_time, connect_end_time

class StatCollection():
    def __init__(self, status, reason, latency, count, total_latency, total_connect_latency, total_bytes):
        self.status = status
        self.reason = reason
        self.latency = latency
        self.count = count
        self.total_latency = total_latency
        self.total_connect_latency = total_connect_latency
        self.total_bytes = total_bytes

        self.agent_start_time = None

        if count > 0:
            self.avg_latency = (total_latency / count)
            self.avg_connect_latency = (total_connect_latency / count)
        else:
            self.avg_latency = 0
            self.avg_connect_latency = 0