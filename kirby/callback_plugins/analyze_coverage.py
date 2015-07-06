
from kirby.serverspec_runner import ServerspecRunner


class CallbackModule(object):
    """Plugin for analyzing task coverage"""

    def playbook_on_start(self):
        self.runner = ServerspecRunner('.', '')

        result = self.runner.run()

        self.num_tests = result[0]
        self.num_failed_tests = result[1]

    def playbook_on_setup(self):
        print "playbook_on_setup"

    def runner_on_ok(self, host, res):
        print "runner_on_ok"

    def playbook_on_task_start(self, name, is_conditional):
        print name

    def playbook_on_stats(self, stats):
        print "playbook_on_stats"
