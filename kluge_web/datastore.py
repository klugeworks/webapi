from __future__ import division
import redis
from kluge_web.io.tokenizer_result_pb2 import TokenizerResultMessage
from kluge_web.io.tokenizer_job_pb2 import TokenizerJobMessage
from collections import defaultdict
import math
import stats
import time


class KlugeRedis():
    def __init__(self, hostname, port, statsd_host, statsd_port):
        self.conn = redis.StrictRedis(host=hostname, port=port, db=0)
        stats.set_statsd(statsd_host, statsd_port)

    def add_job(self, unique_id, chunk_count, lang, job_msg, namespace="kluge"):
        start = time.time()
        self.conn.hset("%s:stt:pb:job:%s" % (namespace, unique_id), str(chunk_count), job_msg.SerializeToString())

        self.conn.lpush("q:in:%s:stt:%s" % (namespace, lang), "%s:%s" % (unique_id, str(chunk_count)))

        self.conn.hset("q:stat:%s:stt:%s" % (namespace, lang),
                       "%s:%s" % (unique_id, str(chunk_count)),
                       "q:in:%s:stt:%s" % (namespace, lang))
        end = time.time()
        stats.incr("add_job")
        stats.timing("add_job", end - start)

    # no need to metric track
    def key_exists(self, keyname):
        return self.conn.exists(keyname)

    # done
    def get_queue_info(self, qname, lang):
        start = time.time()
        keyname = "q:%s:kluge:stt:%s" % (qname, lang)
        if not self.key_exists(keyname):
            return None
        elements = self.conn.lrange(keyname, 0, -1)
        end = time.time()
        stats.incr("get_queue_info")
        stats.timing("get_queue_info", end - start)
        return elements

    # done
    def get_status_info(self, uid, chunkid, lang):
        start = time.time()
        keyname = "q:stat:kluge:stt:%s" % lang
        if not self.key_exists(keyname):
            return None
        status = self.conn.hget(keyname, uid + ":" + chunkid)
        end = time.time()
        stats.incr("get_status_info")
        stats.timing("get_status_info", end - start)
        return status

    # maybe
    def get_transcript_chunk(self, uid, lang, chunkid):
        start = time.time()
        keyname = "kluge:stt:1b:%s:%s" % (lang, uid)
        if not self.key_exists(keyname):
            return None
        transcript_chunk = self.conn.hget(keyname, chunkid)
        end = time.time()
        stats.incr("get_transcript_chunk")
        stats.timing("get_transcript_chunk", end - start)
        return transcript_chunk.strip()

    # maybe
    def get_transcript(self, lang, uid):
        start = time.time()
        keyname = "kluge:stt:1b:%s:%s" % (lang, uid)
        if not self.key_exists(keyname):
            return None
        chunk_ids = self.conn.hkeys(keyname)
        sorted_chunk_ids = sorted(chunk_ids, key=int)
        transcript = ""
        for chunk_id in sorted_chunk_ids:
            transcript = " " + self.conn.hget(keyname, chunk_id)
        end = time.time()
        stats.incr("get_transcript")
        stats.timing("get_transcript", end - start)
        return transcript.strip()

    # maybe
    def get_raw_transcript(self, lang, uid):
        start = time.time()
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
        end = time.time()
        stats.incr("get_raw_transcript")
        stats.timing("get_raw_transcript", end - start)
        return transcript.strip()

    # maybe
    def get_term_freqs_chunk(self, uid, lang, chunkid):
        start = time.time()
        keyname = "kluge:stt:tf:%s:%s:%s" % (lang, uid, chunkid)
        if not self.key_exists(keyname):
            return None
        tfs = self.conn.hgetall(keyname)
        end = time.time()
        stats.incr("get_term_freqs_chunk")
        stats.timing("get_term_freqs_chunk", end - start)
        return tfs

    # maybe
    def get_term_freqs(self, lang, uid):
        start = time.time()
        keyname = "kluge:stt:tf:%s:%s" % (lang, uid)
        if not self.key_exists(keyname):
            return None
        tfs = self.conn.hgetall(keyname)
        end = time.time()
        stats.incr("get_term_freqs")
        stats.timing("get_term_freqs", end - start)
        return tfs

    # maybe
    def get_job_chunks(self, uid):
        start = time.time()
        keyname = "kluge:stt:pb:job:%s" % (uid)
        if not self.key_exists(keyname):
            return None
        chunk_ids = self.conn.hkeys(keyname)
        end = time.time()
        stats.incr("get_job_chunks")
        stats.timing("get_job_chunks", end - start)
        return chunk_ids

    # maybe
    def get_result_chunks(self, uid):
        start = time.time()
        keyname = "kluge:stt:pb:result:%s" % (uid)
        if not self.key_exists(keyname):
            return None
        chunk_ids = self.conn.hkeys(keyname)
        end = time.time()
        stats.incr("get_result_chunks")
        stats.timing("get_result_chunks", end - start)
        return chunk_ids

    # maybe
    def get_word_cloud(self, uid, lang, max_words=50, doc_count=14428):
        start = time.time()
        tf_keyname = "kluge:stt:tf:%s:%s" % (lang, uid)
        df_keyname = "kluge:stt:df:%s:static" % lang

        if not self.key_exists(tf_keyname):
            return None
        if not self.key_exists(df_keyname):
            return None
        tfs = self.conn.hgetall(tf_keyname)
        tf_df = defaultdict(dict)

        temp_tf_df = []

        tf_keys = tfs.keys()
        dfword_counts = self.conn.hmget(df_keyname, *tf_keys)
        for idx, tfword in enumerate(tf_keys):
            dfword_count = dfword_counts[idx]
            try:
                tf = int(tfs[tfword])
                df = int(dfword_count)
                tfidf = tf * math.log10(doc_count/df)
                temp_tf_df.append((tfword, int(tfs[tfword]), int(dfword_count), tfidf))
            except Exception, e:
                print str(e)

        sorted_tf_df = sorted(temp_tf_df, key=lambda tup: tup[3], reverse=True)
        for tup in sorted_tf_df[:max_words]:
            tf_df[tup[0]] = dict(tf=tup[1], df=tup[2], tfidf=tup[3])

        wordcloud_vals = {
            "doc_count": doc_count,
            "tokens": tf_df,
        }
        end = time.time()
        stats.incr("get_word_cloud")
        stats.timing("get_word_cloud", end - start)
        return wordcloud_vals

    # maybe
    def get_word_cloud_chunk(self, uid, lang, chunkid, max_words=30, doc_count=14428):
        start = time.time()
        tf_keyname = "kluge:stt:tf:%s:%s:%s" % (lang, uid, chunkid)
        df_keyname = "kluge:stt:df:%s:static" % lang

        if not self.key_exists(tf_keyname):
            return None
        if not self.key_exists(df_keyname):
            return None
        tfs = self.conn.hgetall(tf_keyname)
        tf_df = defaultdict(dict)

        temp_tf_df = []

        tf_keys = tfs.keys()
        dfword_counts = self.conn.hmget(df_keyname, *tf_keys)
        for idx, tfword in enumerate(tf_keys):
            dfword_count = dfword_counts[idx]
            try:
                tf = int(tfs[tfword])
                df = int(dfword_count)
                tfidf = tf * math.log10(doc_count/df)
                temp_tf_df.append((tfword, int(tfs[tfword]), int(dfword_count), tfidf))
            except Exception, e:
                print str(e)

        sorted_tf_df = sorted(temp_tf_df, key=lambda tup: tup[3], reverse=True)
        for tup in sorted_tf_df[:max_words]:
            tf_df[tup[0]] = dict(tf=tup[1], df=tup[2], tfidf=tup[3])

        wordcloud_vals = {
            "doc_count": doc_count,
            "tokens": tf_df,
        }
        end = time.time()
        stats.incr("get_word_cloud_chunk")
        stats.timing("get_word_cloud_chunk", end - start)
        return wordcloud_vals
