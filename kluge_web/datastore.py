import redis
from kluge_web.io.tokenizer_result_pb2 import TokenizerResultMessage
from kluge_web.io.tokenizer_job_pb2 import TokenizerJobMessage


class KlugeRedis():
    def __init__(self, hostname, port):
        self.conn = redis.StrictRedis(host=hostname, port=port, db=0)

    def get_transcripts(self, queue, num=-1):
        # pull all elements off the queue
        num = max(num, -1)
        tok_results = []
        elements = self.conn.lrange(queue, 0, num)
        for element in elements:
            tok_result = TokenizerResultMessage()
            tok_result.ParseFromString(element)
            tok_results.append(tok_result)
        return tok_results

    def get_jobs(self, queue, num=-1):
        # pull all elements off the queue
        num = max(num, -1)
        jobs = []
        elements = self.conn.lrange(queue, 0, num)
        for element in elements:
            job = TokenizerJobMessage()
            job.ParseFromString(element)
            jobs.append(job)
        return jobs

    def add_job(self, queue, job_msg):
        self.conn.lpush(queue, job_msg.SerializeToString())