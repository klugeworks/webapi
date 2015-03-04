import redis
from kluge_web.io.tokenizer_result_pb2 import TokenizerResultMessage
from kluge_web.io.tokenizer_job_pb2 import TokenizerJobMessage

# Extremely lightweight dictionary wrapper
class TodoDAO():
    def __init__(self):
        self.todo_list = dict()

    def set_todos(self, todos):
        self.todo_list = todos

    def clear_todos(self):
        self.todo_list = dict()


# Exact same object to enable factory testing
class TodoDAO2():
    def __init__(self):
        self.todo_list = dict()

    def set_todos(self, todos):
        self.todo_list = todos

    def clear_todos(self):
        self.todo_list = dict()


class KlugeRedis():
    def __init__(self, hostname, port):
        self.conn = redis.StrictRedis(host=hostname, port=port, db=0)

    def get_transcripts(self, queue, num=-1):
        # pull all elements off the queue
        tok_results = []
        elements = self.conn.lrange(queue, 0, num)
        for element in elements:
            tok_result = TokenizerResultMessage()
            tok_result.ParseFromString(element)
            tok_results.append(tok_result)
        return tok_results

    def get_jobs(self, queue, num=-1):
        # pull all elements off the queue
        jobs = []
        elements = self.conn.lrange(queue, 0, num)
        for element in elements:
            job = TokenizerJobMessage()
            job.ParseFromString(element)
            jobs.append(job)
        return jobs