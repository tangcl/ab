#! -*- encoding:utf-8 -*-
import Queue
import socket
from threading import Thread
from onethread import StatCollection, WhileTread

class LoadManager(Thread):
    def __init__(self, num_agents, runtime_stats):
        Thread.__init__(self)
        socket.setdefaulttimeout(300)
        self.running = True
        self.num_agents = num_agents
        self.runtime_stats = runtime_stats
        for i in range(self.num_agents):
            self.runtime_stats[i] = StatCollection(0, '', 0, 0, 0, 0, 0)
        self.results_queue = Queue.Queue()  #收集单一线程的执行结果
        self.agent_refs = []
        self.request_queue = []

    def run(self):
        self.running = True
        self.agents_started = False
        #并发数num_agents
        for i in range(self.num_agents):
            if self.running:
                agent = WhileTread(i, self.runtime_stats, self.request_queue, self.results_queue)
                agent.start()
                self.agent_refs.append(agent)
        self.agents_started = True

    def stop(self):
        self.running = False
        for agent in self.agent_refs:
            agent.stop()

    def add_req(self, req):
        self.request_queue.append(req)