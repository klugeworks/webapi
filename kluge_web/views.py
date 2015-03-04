import os
from flask import Blueprint, current_app, send_file, send_from_directory
from flask_restful import abort, Resource, reqparse, Api
import werkzeug
import cStringIO
from kluge_web.io.tokenizer_job_pb2 import TokenizerJobMessage
from kluge_web.io.tokenizer_result_pb2 import TokenizerResultMessage
import uuid

api = Api()
blue = Blueprint('main', __name__, None)


@blue.route('/')
def index():
    conf_app_name = current_app.config.get('KLUGE_WEB_APP_NAME', 'ASR transcript demo')
    return conf_app_name


class RawTranscript(Resource):
    @staticmethod
    def get(uid, lang):
        transcript = current_app.kluge_web_datastore.get_test_transcript(lang, uid)
        if transcript is None:
            return abort(404, message="Language or uuid doesn't exists")
        return transcript


class Transcript(Resource):
    @staticmethod
    def get(uid, lang):
        transcript = current_app.kluge_web_datastore.get_transcript(lang, uid)
        if transcript is None:
            return abort(404, message="Language or uuid doesn't exists")
        return transcript


class TranscriptChunk(Resource):
    @staticmethod
    def get(uid, lang, chunkid):
        transcript = current_app.kluge_web_datastore.get_transcript_chunk(uid, lang, chunkid)
        if transcript is None:
            return abort(404, message="Language, uuid or chunkid doesn't exists")
        return transcript


class TermFreqs(Resource):
    @staticmethod
    def get(uid, lang):
        tfs = current_app.kluge_web_datastore.get_term_freqs(lang, uid)
        if tfs is None:
            return abort(404, message="Language or uuid doesn't exist")
        return tfs


class TermFreqsChunk(Resource):
    @staticmethod
    def get(uid, lang, chunkid):
        tfs = current_app.kluge_web_datastore.get_term_freqs_chunk(uid, lang, chunkid)
        if tfs is None:
            return abort(404, message="Language, uuid or chunkid doesn't exist")
        return tfs


class QueueInfo(Resource):
    @staticmethod
    def get(lang, qname):
        elements = current_app.kluge_web_datastore.get_queue_info(qname, lang)
        # Elements is none when the key is not found
        if elements is None:
            return abort(404, message="Queue name or language doesn't exist")
        return elements


class StatusInfo(Resource):
    @staticmethod
    def get(uid, chunkid, lang):
        status = current_app.kluge_web_datastore.get_status_info(uid, chunkid, lang)
        if status is None:
            return abort(404, message="Language, uuid or chunkid doesn't exists")
        return status


class GetChunks(Resource):
    @staticmethod
    def get(uid):
        chunk_ids = current_app.kluge_web_datastore.get_job_chunks(uid)
        if chunk_ids is None:
            return abort(404, message="UUID doesn't exists")
        return chunk_ids


class GetSpecificChunks(Resource):
    @staticmethod
    def get(uid, ttype):
        if ttype == "jobs":
            chunk_ids = current_app.kluge_web_datastore.get_job_chunks(uid)
        elif ttype == "results":
            chunk_ids = current_app.kluge_web_datastore.get_result_chunks(uid)
        else:
            chunk_ids = []
        if chunk_ids is None:
            return abort(404, message="UUID doesn't exists")
        return chunk_ids


class GetWordclouds(Resource):
    @staticmethod
    def get(uid, lang):
        word_cloud = current_app.kluge_web_datastore.get_word_cloud(uid, lang)
        if word_cloud is None:
            return abort(404, message="UUID or lang doesn't exists")
        return word_cloud


# Mock file download
class FileDown(Resource):
    @staticmethod
    def get():
        src_directory = os.path.dirname(os.path.realpath(__file__))
        outbound_file = "%s/%s" % (src_directory, "__init__.py")
        return send_file(outbound_file)

# From file uploads
upload_parser = reqparse.RequestParser()
upload_parser.add_argument('bytes', type=werkzeug.datastructures.FileStorage, location='files')
upload_parser.add_argument('chunkid', type=int, default=1)
upload_parser.add_argument('uuid', type=str)
upload_parser.add_argument('name', type=str, required=True)
upload_parser.add_argument('namespace', type=str, default='kluge')


# Job upload
class AddJob(Resource):
    def __init__(self):
        self.redis_conn = current_app.kluge_web_datastore

    def post(self, lang):
        available_languages = set(['english'])
        if not lang in available_languages:
            return abort(404, message="Language not available for processing")

        args = upload_parser.parse_args()
        bytes = args['bytes']
        chunkid = args['chunkid']
        uid = args['uuid']
        name = args['name']
        namespace = args['namespace']

        if not uid:
            uid = str(uuid.uuid4())

        data_array = bytes.read()

        job = TokenizerJobMessage()
        job.uid = uid
        job.language = lang
        job.chunk = chunkid
        job.audio_uri = name
        job.raw_audio = data_array
        job.format = TokenizerJobMessage.UL
        job.sample_rate = 8000
        job.sample_size = 8

        self.redis_conn.add_job(uid, chunkid, lang, job, namespace=namespace)
        return dict(docid=uid, chunkid=chunkid), 200


##
## Actually setup the Api resource routing here
##
api.add_resource(RawTranscript, '/rawtrans/<string:uid>/<string:lang>')
api.add_resource(Transcript, '/transcript/<string:uid>/<string:lang>')
api.add_resource(TranscriptChunk, '/transcript/<string:uid>/<string:lang>/<string:chunkid>')
api.add_resource(TermFreqs, '/tfs/<string:uid>/<string:lang>')
api.add_resource(TermFreqsChunk, '/tfs/<string:uid>/<string:lang>/<int:chunkid>')
api.add_resource(QueueInfo, '/queue/<string:lang>/<string:qname>')
api.add_resource(StatusInfo, '/status/<string:uid>/<string:chunkid>/<string:lang>')
api.add_resource(GetChunks, '/doc/<string:uid>/')
api.add_resource(GetSpecificChunks, '/doc/<string:uid>/<string:ttype>')
api.add_resource(GetWordclouds, '/doc/<string:uid>/<string:lang>/wordcloud')

#api.add_resource(FileDown, '/file')
api.add_resource(AddJob, '/jobs/<string:lang>')