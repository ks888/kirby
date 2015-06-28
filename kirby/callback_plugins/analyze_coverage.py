

class CallbackModule(object):
    """Plugin for analyzing task coverage"""

    def __init__(self):
        pass

    def playbook_on_task_start(self, name, is_conditional):
        print name
        print is_conditional
