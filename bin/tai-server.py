
import tornado.ioloop
import tornado.web
from tornado.escape import json_decode, json_encode
import os.path
import sys
import json

class Query(tornado.web.RequestHandler):

    def prepare(self):
        header = "Content-Type"
        body = "application/json"
        self.set_header(header, body)

    def post(self):
        query = json_decode(self.request.body)
        if 'uuid' in query:
           if query['uuid'] in tai_full:
              result = tai_full[query['uuid']]
           else:
              result = {'error': 'UUID is not known in the MISP galaxy threat-actor'}
        if 'name' in query:
           if query['name'].lower() not in tai_names:
              result = {'error': 'Name or synomym is not known in the MISP galaxy threat-actor'}
              return self.write("{}".format(json.dumps(result)))
           for uuid in tai_names[query['name'].lower()]:
               result = []
               result.append(tai_full[uuid])
        return self.write("{}".format(json.dumps(result)))

class Get(tornado.web.RequestHandler):

    def prepare(self):
        header = "Content-Type"
        body = "application/json"
        self.set_header(header, body)

    def get(self, uuid):
        if uuid in tai_full:
           result = tai_full[uuid]
        else:
           result = {'error': 'UUID is not known in the MISP galaxy threat-actor'}
        return self.write("{}".format(json.dumps(result)))


application = tornado.web.Application([
    (r"/query", Query),
    (r"/get/(.*)", Get)
])

if not (os.path.exists('../misp-galaxy/clusters/threat-actor.json')):
    sys.exit("Missing threat-actor.json MISP galaxy, did you git submodule init/update?")

with open('../misp-galaxy/clusters/threat-actor.json', 'rb') as galaxyta:
    threat_actors = json.load(galaxyta)

tai_full = {}
tai_names = {}

for threat_actor in threat_actors['values']:
        tai_full[threat_actor['uuid']] = threat_actor
        tai_names[threat_actor['value'].lower()] = []
        tai_names[threat_actor['value'].lower()].append(threat_actor['uuid'])
        if 'meta' in threat_actor:
           if 'synonyms' in threat_actor['meta']:
              for synonym in threat_actor['meta']['synonyms']:
                  if not synonym.lower() in tai_names:
                      tai_names[synonym.lower()] = []
                  tai_names[synonym.lower()].append(threat_actor['uuid'])


if __name__ == "__main__":
    application.listen(8889)
    tornado.ioloop.IOLoop.instance().start()



