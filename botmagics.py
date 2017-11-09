import bclient
import time
from IPython.core.magic import (Magics, magics_class, line_magic)
from IPython.core.display import (display, HTML)

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
        display(HTML("<font color='blue'><b>{0}</b></font>".format(activity.get("text", ""))))
        return activity

    def _ensure_conversation(self):
        if not self.conversation:
            display
    
    @line_magic
    def connect(self, auth_key):
        self.conversation = bclient.Client(auth_key).start_conversation()
        display(HTML("<b>Started conversation with ID: {0}</b>".format(self.conversation.conv_id)))
        self._poll_for_response()

    @line_magic
    def attach(self, file_path):
        self._ensure_conversation()
        self.conversation.upload_image_file(file_path)
        display(HTML("<img src='{0}'>".format(file_path)))
        self._poll_for_response()

    @line_magic
    def post(self, text):
        self._ensure_conversation()
        # Render images if possible
        import urlparse, os
        url = urlparse.urlparse(text)
        if url.scheme.startswith("http"):
            ext = os.path.splitext(url.path)[1][1:]
            if ext.lower() in ("jpg", "png", "gif", "jpeg"):
                display(HTML("<img src='{0}'>".format(text)))
                
        activity = {"type":"message", "text": text, "from": {"id": self.conversation.user_id}, "locale":"en-US", "textFormat":"plain"}
        self.conversation.post_activity(activity)
        self._poll_for_response()

    @line_magic
    def done(self, text):
        self._ensure_conversation()
        self.conversation.close()
        display(HTML("<b>Good bye!</b>"))
        self.conversation = None
        
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
