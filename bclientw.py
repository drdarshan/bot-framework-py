import httplib
import json
import urlparse
from contextlib import closing

DIRECTLINE_URL="https://directline.botframework.com/v3/directline"

class Conversation(object):
    def __init__(self, client, conv_id, user_id = "user1"):
        self.client = client
        self.conv_id = conv_id
        self.user_id = user_id

    def get_activities(self, index = -1):
        data = self.client._make_request("GET", "conversations/{0}/activities".format(self.conv_id))
        activities = data["activities"]
        return {} if activities == [] else activities[index]

    def post_activity(self, activity):
        data = self.client._make_request("POST", \
                                         "conversations/{0}/activities".format(self.conv_id),\
                                         json=activity)
        return data["id"]

    def upload_image_file(self, file_path):
        import os
        ext = os.path.splitext(file_path)[1][1:]
        mime_type = "image/"+ext
        with open(file_path, "rb") as f:
            image_data = f.read()         

        extra_headers = {'Content-Type': mime_type,
                         'Context-Disposition': 'name="file"; filename={0}'.format(file_path)}

        data = self.client._make_request("POST",
                                         "conversations/{0}/upload?userId={1}".format(self.conv_id, self.user_id),
                                         data=image_data,
                                         extra_headers=extra_headers)
        return data["id"]

    def upload_image_url(self, url):
        activity = {"type":"message",
                    "text": url,
                    "from": {"id": self.user_id},
                    "locale":"en-US",
                    "textFormat":"plain"}
        return self.post_activity(activity)
    
    def close(self):
        activity = {'type': 'endOfConversation', "from": {"id":self.user_id}}
        return self.post_activity(activity)

    def __str__(self):
        return "Conversation ID: "+self.conv_id

    def __repr__(self):
        return str(self)

class Client(object):
    def _make_request(self, method, url, **kwargs):
        import requests
        url = '/'.join((DIRECTLINE_URL, url))
        
        extra_headers = kwargs.get("extra_headers", None)
        if extra_headers:
            headers = self.headers.copy()
            headers.update(extra_headers)
            del(kwargs['extra_headers'])
        else:
            headers = self.headers
        kwargs["headers"] = headers

        print url
        response = requests.request(method, url, **kwargs)
        print response
        response.raise_for_status()
        return response.json()

    def __init__(self, access_key, user_id = "user1"):
        self.access_key = access_key
        self.user_id = user_id
        self.headers = {'Authorization': 'Bearer ' + access_key}

    def get_token(self):
        return self._make_request("POST", "tokens/generate")["token"]

    def start_conversation(self):
        data = self._make_request("POST", "conversations")
        print data
        return Conversation(self, data["conversationId"], self.user_id)
