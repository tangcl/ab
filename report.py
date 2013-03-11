#! -*- encoding:utf-8 -*-
class RuntimeReporter(object):
    def __init__(self, runtime_stats):
        self.runtime_stats = runtime_stats
        self.last_count = 0

    def refresh(self, elapsed_secs, refresh_rate):
        ids = self.runtime_stats.keys()
        agg_count = sum([self.runtime_stats[id].count for id in ids if id != -1])  # total req count
        agg_total_latency = sum([self.runtime_stats[id].total_latency for id in ids if id != -1])
        total_bytes_received = sum([self.runtime_stats[id].total_bytes for id in ids if id!= -1])
        avg_resp_time = avg_throughput = interval_count = cur_throughput = 0
        if agg_count > 0 and elapsed_secs > 0:
            avg_resp_time = agg_total_latency / agg_count  # 总的获取response的时间
            avg_throughput = float(agg_count) / elapsed_secs  # 平均吞吐量,总的请求数/请求时间
        server_software = [self.runtime_stats[id]["serversoftware"] for id in ids if id == -1][0]
        print "server software:\t",server_software
        document_len = [self.runtime_stats[id]["documentlength"] for id in ids if id == -1][0]
        print "document_length\t",document_len
        print "Complete requests:\t",agg_count
        print "Time per request:\t", avg_resp_time
        print "Requests per seconds:\t", avg_throughput
        print "Transfer rate:\t", total_bytes_received
