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