import redis
from kluge_web.io.tokenizer_result_pb2 import TokenizerResultMessage
from kluge_web.io.tokenizer_job_pb2 import TokenizerJobMessage
from collections import defaultdict


class KlugeRedis():
    def __init__(self, hostname, port):
        self.conn = redis.StrictRedis(host=hostname, port=port, db=0)

    def add_job(self, queue, job_msg):
        self.conn.lpush(queue, job_msg.SerializeToString())

    # done
    def key_exists(self, keyname):
        return self.conn.exists(keyname)

    # done
    def get_queue_info(self, qname, lang):
        keyname = "q:%s:kluge:stt:%s" % (qname, lang)
        if not self.key_exists(keyname):
            return None
        elements = self.conn.lrange(keyname, 0, -1)
        return elements

    # done
    def get_status_info(self, uid, chunkid, lang):
        keyname = "q:stat:kluge:stt:%s" % lang
        if not self.key_exists(keyname):
            return None
        status = self.conn.hget(keyname, uid + ":" + chunkid)
        return status

    # maybe
    def get_transcript_chunk(self, uid, lang, chunkid):
        keyname = "kluge:stt:1b:%s:%s" % (lang, uid)
        if not self.key_exists(keyname):
            return None
        transcript_chunk = self.conn.hget(keyname, chunkid)
        return transcript_chunk

    # maybe
    def get_transcript(self, lang, uid):
        keyname = "kluge:stt:1b:%s:%s" % (lang, uid)
        if not self.key_exists(keyname):
            return None
        chunk_ids = self.conn.hkeys(keyname)
        sorted_chunk_ids = sorted(chunk_ids, key=int)
        transcript = ""
        for chunk_id in sorted_chunk_ids:
            transcript += " " + self.conn.hget(keyname, chunk_id)
        return transcript

    # maybe
    def get_raw_transcript(self, lang, uid):
        keyname = "kluge:stt:pb:result:%s" % (uid)
        if not self.key_exists(keyname):
            return None
        chunk_ids = self.conn.hkeys(keyname)
        sorted_chunk_ids = sorted(chunk_ids, key=int)
        transcript = ""
        for chunk_id in sorted_chunk_ids:
            element = self.conn.hget(keyname, chunk_id)
            tok_result = TokenizerResultMessage()
            tok_result.ParseFromString(element)
            transcript += " " + tok_result.word_transcript
        return transcript

    # maybe
    def get_term_freqs_chunk(self, uid, lang, chunkid):
        keyname = "kluge:stt:tf:%s:%s:%s" % (lang, uid, chunkid)
        if not self.key_exists(keyname):
            return None
        tfs = self.conn.hgetall(keyname)
        return tfs

    # maybe
    def get_term_freqs(self, lang, uid):
        keyname = "kluge:stt:tf:%s:%s" % (lang, uid)
        if not self.key_exists(keyname):
            return None
        tfs = self.conn.hgetall(keyname)
        return tfs

    # maybe
    def get_job_chunks(self, uid):
        keyname = "kluge:stt:pb:job:%s" % (uid)
        if not self.key_exists(keyname):
            return None
        chunk_ids = self.conn.hkeys(keyname)
        return chunk_ids

    # maybe
    def get_result_chunks(self, uid):
        keyname = "kluge:stt:pb:result:%s" % (uid)
        if not self.key_exists(keyname):
            return None
        chunk_ids = self.conn.hkeys(keyname)
        return chunk_ids