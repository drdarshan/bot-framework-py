import httplib
import json
from contextlib import closing

DIRECTLINE_URL="directline.botframework.com"
ACCESS_KEY="XNNK-LxnABc.cwA.wBg.JRK3epX-idsrD_h16cu1hlac1KUcAXLkVc7m-m9Sxx0"
HEADERS={'Authorization': 'Bearer ' + ACCESS_KEY}

def _make_request(url, body=None, extra_headers=None, method="POST"):
    with closing(httplib.HTTPSConnection(DIRECTLINE_URL)) as conn:
        #json_body = body and json.dumps(body)
        if extra_headers:
            headers = HEADERS.copy()
            headers.update(extra_headers)
        else:
            headers = HEADERS
            
        conn.request(method, url, body, headers=headers)
        response = conn.getresponse()
        assert response.status == 200 or response.status == 201
        return json.loads(response.read())

def get_token():
    data = _make_request("/v3/directline/tokens/generate")
    return data["token"]

def create_conversation():
    data = _make_request("/v3/directline/conversations")
    return data["conversationId"]

def get_activities(converstation_id, index=-1):
    data = _make_request("/v3/directline/conversations/"+converstation_id+"/activities", method="GET")
    print data
    return data["activities"][index]["text"]

def send_activity(conversation_id, activity):
    data = _make_request("/v3/directline/conversations/"+conversation_id+"/activities", body=activity)
    return data["id"]

def close_converation(conversation_id):
    return send_activity(conversation_id, json.dumps({'type': 'endOfConversation'}))

def upload_image(converstation_id, user_id, file_path):
    import os
    import base64
    ext = os.path.splitext(file_path)[1][1:]
    mime_type = "image/"+ext
    with open(file_path, "rb") as f:
        image_data = f.read() #base64.b64encode(f.read())
        
    extra_headers = {'Content-Type': mime_type, 'Context-Disposition': 'name="file"; filename={0}'.format(file_path)}
    data = _make_request("/v3/directline/conversations/{0}/upload?userId={1}".format(converstation_id, user_id),\
                         body=image_data,\
                         extra_headers=extra_headers)
    return data["id"]

