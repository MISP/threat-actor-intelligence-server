
import tornado.ioloop
import tornado.web

from tornado.escape import json_decode, json_encode
from tornado.options import define, options
import os.path
import sys
import json
import datetime

define('port', default=8889, help='port to listen on')
define('address', default='0.0.0.0', help='address to listen on')

web_dir = os.path.join(os.path.dirname(__file__), "..", "web")

class Query(tornado.web.RequestHandler):

    def prepare(self):
        header = "Content-Type"
        body = "application/json"
        self.set_header(header, body)

    def post(self):
        query = json_decode(self.request.body)
        if not ('uuid' in query or 'name' in query or 'country' in query):
            return self.write(json.dumps("'error': 'Incorrect query format'"))
        user_agent = self.request.headers["User-Agent"]
        if 'uuid' in query:
           if query['uuid'] in tai_full:
              result = tai_full[query['uuid']]
           else:
              result = {'error': 'UUID is not known in the MISP galaxy threat-actor'}
        if 'name' in query:
           if query['name'].lower() not in tai_names:
              result = {'error': 'Name or synomym is not known in the MISP galaxy threat-actor'}
              return self.write("{}".format(json.dumps(result)))
           result = []
           for uuid in tai_names[query['name'].lower()]:
               result.append(tai_full[uuid])
        if 'country' in query:
            if query['country'].lower() in tai_country:
               ta = tai_country[query['country'].lower()]
               result = []
               for uuid in tai_country[query['country'].lower()]:
                   result.append(tai_full[uuid])
            else:
                result = {'error': 'Not existing country in the MISP galaxy threat-actor'}
        print("Query {} from {}".format(query, user_agent))
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

class Info(tornado.web.RequestHandler):

     def get(self):
        return self.write("{}".format(json.dumps(tai_info)))

application = tornado.web.Application([
    (r"/query", Query),
    (r"/get/(.*)", Get),
    (r"/info", Info),

    # Static handler: serve web/ at app root
    (r"/(.*)", tornado.web.StaticFileHandler, {"path": web_dir, "default_filename": "index.html"}),
])

if not (os.path.exists('../misp-galaxy/clusters/threat-actor.json')):
    sys.exit("Missing threat-actor.json MISP galaxy, did you git submodule init/update?")

with open('../misp-galaxy/clusters/threat-actor.json', 'rb') as galaxyta:
    threat_actors = json.load(galaxyta)

tai_full = {}
tai_names = {}
tai_info = {}
tai_country = {}

tai_info['version'] = threat_actors['version']
tai_info['number_actors'] = 0
tai_info['number_synonyms'] = 0
tai_info['started'] = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")

for threat_actor in threat_actors['values']:
        tai_full[threat_actor['uuid']] = threat_actor
        tai_names[threat_actor['value'].lower()] = []
        tai_names[threat_actor['value'].lower()].append(threat_actor['uuid'])
        tai_info['number_actors'] += 1
        if 'meta' in threat_actor:
           if 'synonyms' in threat_actor['meta']:
              for synonym in threat_actor['meta']['synonyms']:
                  if not synonym.lower() in tai_names:
                      tai_names[synonym.lower()] = []
                  tai_names[synonym.lower()].append(threat_actor['uuid'])
                  tai_info['number_synonyms'] += 1
           if 'country' in threat_actor['meta']:
              if not threat_actor['meta']['country'].lower() in tai_country:
                  tai_country[threat_actor['meta']['country'].lower()] = []
              tai_country[threat_actor['meta']['country'].lower()].append(threat_actor['uuid'])

if __name__ == "__main__":
    tornado.options.parse_command_line()
    application.listen(options.port, address=options.address)
    tornado.ioloop.IOLoop.instance().start()
