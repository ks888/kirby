

class ServerspecRunner(object):
    """Run serverspec command and retrieve its results"""

    def __init__(self, serverspec_dir, serverspec_cmd):
        self.serverspec_dir = serverspec_dir
        self.serverspec_cmd = serverspec_cmd

    def run(self):
        return None
