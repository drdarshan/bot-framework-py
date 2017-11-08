import httplib
import json
from contextlib import closing

DIRECTLINE_URL="directline.botframework.com"
ACCESS_KEY="XNNK-LxnABc.cwA.wBg.JRK3epX-idsrD_h16cu1hlac1KUcAXLkVc7m-m9Sxx0"
HEADERS={'Authorization': 'Bearer ' + ACCESS_KEY}

def _make_request(url, body=None, extra_headers=None, method="POST"):
    with closing(httplib.HTTPSConnection(DIRECTLINE_URL)) as conn:
        if extra_headers:
            headers = HEADERS.copy()
            headers.update(extra_headers)
        else:
            headers = HEADERS

        conn.request(method, url, body, headers=headers)
        response = conn.getresponse()
        print response.status, response.reason
        r = response.read()
        assert response.status == 200 or response.status == 201
        return json.loads(r)

def get_token():
    data = _make_request("/v3/directline/tokens/generate")
    return data["token"]

def create_conversation():
    data = _make_request("/v3/directline/conversations")
    return data["conversationId"]

def get_activities(converstation_id, index=-1):
    data = _make_request("/v3/directline/conversations/"+converstation_id+"/activities", method="GET")
    return data["activities"][index] #["text"]

def send_activity(conversation_id, activity):
    extra_headers = {'Content-Type': "application/json"}
    data = _make_request("/v3/directline/conversations/"+conversation_id+"/activities", body=activity, extra_headers=extra_headers)
    return data["id"]

def close_converation(conversation_id):
    return send_activity(conversation_id, json.dumps({'type': 'endOfConversation', "from": {"id":"user1"}}))

def upload_image_file(converstation_id, user_id, file_path):
    import os
    ext = os.path.splitext(file_path)[1][1:]
    mime_type = "image/"+ext
    with open(file_path, "rb") as f:
        image_data = f.read() 
        
    extra_headers = {'Content-Type': mime_type, 'Context-Disposition': 'name="file"; filename={0}'.format(file_path)}
    data = _make_request("/v3/directline/conversations/{0}/upload?userId={1}".format(converstation_id, user_id),\
                         body=image_data,\
                         extra_headers=extra_headers)
    return data["id"]

def upload_image_url(conversation_id, user_id, url):
    import os
    import urlparse
    import json
    ext = os.path.splitext(urlparse.urlsplit(url).path)[1][1:]
    mime_type = "image/"+ext
    extra_headers = {'Content-Type': "application/json"}
    activity = {"type":"message", "text": url, "from": {"id": "user1"}, "locale":"en-US", "textFormat":"plain"}
    data = _make_request("/v3/directline/conversations/{0}/activities".format(conversation_id), body=json.dumps(activity), extra_headers=extra_headers)
    return data["id"]
