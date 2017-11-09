import bclient
import time
from IPython.core.magic import (Magics, magics_class, line_magic)

# The class MUST call this class decorator at creation time
@magics_class
class BotMagics(Magics):
    def __init__(self, shell):
        super(BotMagics, self).__init__(shell)
        self.conversation = None

    def _poll_for_response(self):
        sender = self.conversation.user_id
        while sender == self.conversation.user_id:
            time.sleep(0.2)
            activity = self.conversation.get_activities()
            sender = activity.get("from", {"id": self.conversation.user_id})["id"]
        return activity
    
    @line_magic
    def connect(self, auth_key):
        self.conversation = bclient.Client(auth_key).start_conversation()
        print self.conversation
        return self._poll_for_response()

    @line_magic
    def upload(self, file_path):
        self.conversation.upload_image_file(file_path)
        return self._poll_for_response()

    @line_magic
    def post(self, text):
        activity = {"type":"message", "text": text, "from": {"id": self.conversation.user_id}, "locale":"en-US", "textFormat":"plain"}
        self.conversation.post_activity(activity)
        return self._poll_for_response()
        

def load_ipython_extension(ipython):
    """
    Any module file that define a function named `load_ipython_extension`
    can be loaded via `%load_ext module.path` or be configured to be
    autoloaded by IPython at startup time.
    """
    # You can register the class itself without instantiating it.  IPython will
    # call the default constructor on it.
    magics = BotMagics(ipython)
    ipython.register_magics(magics)
