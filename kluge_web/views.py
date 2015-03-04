import os
from flask import Blueprint, current_app, send_file
from flask_restful import abort, Resource, reqparse, Api
import werkzeug
import cStringIO
import redis
from kluge_web.io.tokenizer_job_pb2 import TokenizerJobMessage

api = Api()
blue = Blueprint('main', __name__, None)


@blue.route('/')
def index():
    conf_app_name = current_app.config.get('KLUGE_WEB_APP_NAME', 'ASR transcript demo\n')
    return conf_app_name


# Mock file download
class FileDown(Resource):
    @staticmethod
    def get():
        src_directory = os.path.dirname(os.path.realpath(__file__))
        outbound_file = "%s/%s" % (src_directory, "__init__.py")
        return send_file(outbound_file)

# From file uploads
parser2 = reqparse.RequestParser()
parser2.add_argument('filein', type=werkzeug.datastructures.FileStorage, location='files')
parser2.add_argument('docid', type=str, location='form')


# Mock file upload
class FileUp(Resource):
    @staticmethod
    def post():
        args = parser2.parse_args()
        fstore = args['filein']
        docid = args['docid']
        data_array = bytearray(fstore.read())
        output = cStringIO.StringIO()
        output.write(data_array)
        output.seek(0)
        return send_file(output)

##
## Actually setup the Api resource routing here
##
api.add_resource(FileDown, '/file')
api.add_resource(FileUp, '/fileup')


# Transcripts argparse
transcripts_args = reqparse.RequestParser()
transcripts_args.add_argument('queue', type=str, required=True)
transcripts_args.add_argument('num', type=int, default=-1)


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
        args = transcripts_args.parse_args()
        queue = args['queue']
        num = args['num']
        redis_connection = current_app.kluge_web_datastore
        transcripts = redis_connection.get_transcripts(queue, num - 1)
        words = [(t.uid, t.word_transcript) for t in transcripts]
        return words, 201


# Transcripts argparse
jobs_args = reqparse.RequestParser()
jobs_args.add_argument('queue', type=str, required=True)
jobs_args.add_argument('num', type=int, default=-1)


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
        args = jobs_args.parse_args()
        queue = args['queue']
        num = args['num']
        redis_connection = current_app.kluge_web_datastore
        jobs = redis_connection.get_jobs(queue, num - 1)
        job_ids = [(j.uid, TokenizerJobMessage.AudioFormat.Name(j.format)) for j in jobs]
        return job_ids, 201

api.add_resource(Transcripts, '/transcripts')
api.add_resource(Jobs, '/jobs')