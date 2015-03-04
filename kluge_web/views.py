import os
from flask import Blueprint, current_app, send_file
from flask_restful import abort, Resource, reqparse, Api
import werkzeug
import cStringIO
from kluge_web.io.tokenizer_job_pb2 import TokenizerJobMessage
from kluge_web.io.tokenizer_result_pb2 import TokenizerResultMessage

api = Api()
blue = Blueprint('main', __name__, None)


@blue.route('/')
def index():
    conf_app_name = current_app.config.get('KLUGE_WEB_APP_NAME', 'ASR transcript demo')
    return conf_app_name


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
upload_parser.add_argument('name', type=str, required=True)
upload_parser.add_argument('language', type=str, default='english')
upload_parser.add_argument('queue', type=str, required=True)


# Mock file upload
class FileUp(Resource):
    @staticmethod
    def post():
        args = upload_parser.parse_args()
        bytes = args['bytes']
        chunkid = args['chunkid']
        name = args['name']
        language = args['language']
        queue = args['queue']

        print bytes

        #data_array = bytearray(bytes.read())
        data_array = bytes.read()
        #output = cStringIO.StringIO()
        #output.write(data_array)

        job = TokenizerJobMessage()
        job.uid = name
        job.language = language
        job.chunk = chunkid
        job.audio_uri = name
        job.raw_audio = data_array
        job.format = TokenizerJobMessage.UL
        job.sample_rate = 8000
        job.sample_size = 8

        redis_connection = current_app.kluge_web_datastore
        redis_connection.add_job(queue, job)
        return name, 200

##
## Actually setup the Api resource routing here
##
api.add_resource(FileDown, '/file')
api.add_resource(FileUp, '/fileup')


# Transcripts argparse
transcripts_parser = reqparse.RequestParser()
transcripts_parser.add_argument('queue', type=str, required=True)
transcripts_parser.add_argument('num', type=int, default=-1)


# Transcripts
#   pull all transcripts on completed redis queue
class Transcripts(Resource):
    @staticmethod
    def get():
        redis_connection = current_app.kluge_web_datastore
        transcripts = redis_connection.get_transcripts('english_results', 5)
        words = [(t.uid, t.word_transcript) for t in transcripts]
        return words, 201

    @staticmethod
    def post():
        args = transcripts_parser.parse_args()
        queue = args['queue']
        num = args['num']
        redis_connection = current_app.kluge_web_datastore
        transcripts = redis_connection.get_transcripts(queue, num - 1)
        words = [(t.uid, t.word_transcript) for t in transcripts]
        return words, 201


# Transcripts argparse
jobs_parser = reqparse.RequestParser()
jobs_parser.add_argument('queue', type=str, required=True)
jobs_parser.add_argument('num', type=int, default=-1)


# Jobs
#   pull all jobs on task redis queue
class Jobs(Resource):
    @staticmethod
    def get():
        redis_connection = current_app.kluge_web_datastore
        jobs = redis_connection.get_jobs('english_audio', 5)
        job_ids = [(j.uid, TokenizerJobMessage.AudioFormat.Name(j.format)) for j in jobs]
        return job_ids

    @staticmethod
    def post():
        args = jobs_parser.parse_args()
        queue = args['queue']
        num = args['num']
        redis_connection = current_app.kluge_web_datastore
        jobs = redis_connection.get_jobs(queue, num - 1)
        job_ids = [(j.uid, TokenizerJobMessage.AudioFormat.Name(j.format)) for j in jobs]
        return job_ids, 201

api.add_resource(Transcripts, '/transcripts')
api.add_resource(Jobs, '/jobs')