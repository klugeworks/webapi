import os
from flask import Blueprint, current_app, send_file
from flask_restful import abort, Resource, reqparse, Api
import werkzeug
import cStringIO

api = Api()
blue = Blueprint('main', __name__, None)


@blue.route('/')
def index():
    conf_app_name = current_app.config.get('KLUGE_WEB_APP_NAME', 'TODO APPLICATION')
    return conf_app_name


def abort_if_todo_doesnt_exist(todo, todo_id):
    if todo_id not in todo.todo_list:
        abort(404, message="Todo {} doesn't exist".format(todo_id))

parser = reqparse.RequestParser()
parser.add_argument('task', type=str)


# Todo
#   show a single todo item and lets you delete them
class Todo(Resource):
    @staticmethod
    def get(todo_id):
        todo = current_app.kluge_web_datastore
        abort_if_todo_doesnt_exist(todo, todo_id)
        return todo.todo_list[todo_id]

    @staticmethod
    def delete(todo_id):
        todo = current_app.kluge_web_datastore
        abort_if_todo_doesnt_exist(todo, todo_id)
        del todo.todo_list[todo_id]
        return '', 204

    @staticmethod
    def put(todo_id):
        todo = current_app.kluge_web_datastore
        args = parser.parse_args()
        task = {'task': args['task']}
        todo.todo_list[todo_id] = task
        return task, 201


# TodoList
#   shows a list of all todos, and lets you POST to add new tasks
class TodoList(Resource):
    @staticmethod
    def get():
        todo = current_app.kluge_web_datastore
        return todo.todo_list

    @staticmethod
    def post():
        todo = current_app.kluge_web_datastore
        args = parser.parse_args()
        todo_id = 'todo%d' % (len(todo.todo_list) + 1)
        todo.todo_list[todo_id] = {'task': args['task']}
        return todo.todo_list[todo_id], 201


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
api.add_resource(TodoList, '/todos')
api.add_resource(Todo, '/todos/<string:todo_id>')
api.add_resource(FileDown, '/file')
api.add_resource(FileUp, '/fileup')