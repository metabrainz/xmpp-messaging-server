from xml.etree import ElementTree as ET
from webserver.jid import JID
import requests
import random
import base64
import uuid

TLS_XMLNS = 'urn:ietf:params:xml:ns:xmpp-tls'
SASL_XMLNS = 'urn:ietf:params:xml:ns:xmpp-sasl'
BIND_XMLNS = 'urn:ietf:params:xml:ns:xmpp-bind'
SESSION_XMLNS = 'urn:ietf:params:xml:ns:xmpp-session'


class BOSHClient:

    def __init__(self, jabberid, password, bosh_service):
        self.rid = random.randint(0, 10000000)  # FIXME: This doesn't look right
        self.jid = JID(jabberid)
        self.password = password
        self.authid = None
        self.sid = None
        self.logged_in = False
        self.headers = {
            "Content-type": "text/xml; charset=utf-8",
            "Accept": "text/xml",
        }
        self.bosh_service = bosh_service

    def build_body(self, child=None):
        """Build a BOSH body."""
        self.rid += 1
        body = ET.Element("body", {
            "xmlns": "http://jabber.org/protocol/httpbind",
            "content": "text/xml; charset=utf-8",
            "xml:lang": "en",
            "rid": str(self.rid),
            "sid": self.sid,
        })
        if child is not None:
            body.append(child)
        return body

    def send_body(self, body):
        # TODO: get rid of this ugly hack
        body_str = ET.tostring(body, encoding="utf8", method="xml")[len("<?xml version='1.0' encoding='utf8'?>")+1:]
        r = requests.post(self.bosh_service,
                          data=body_str,
                          headers=self.headers)
        if r.status_code == 200:
            resp_xml = ET.fromstring(r.text)
            return resp_xml, list(resp_xml)
        else:
            # TODO: Do this properly:
            raise Exception("HALP")

    def start_session_and_auth(self, hold="1", wait="60"):
        body = ET.Element("body", {
            "content": "text/xml; charset=utf-8",
            "xmlns": "http://jabber.org/protocol/httpbind",
            "xmlns:xmpp": "urn:xmpp:xbosh",
            "xml:lang": "en",
            "xmpp:version": "1.0",
            "rid": str(self.rid),
            "to": self.jid.domainpart,
            "hold": hold,
            "wait": wait,
        })

        retb, elems = self.send_body(body)

        if type(retb) != str and retb.get('authid') and retb.get('sid'):
            self.authid = retb.get('authid')
            self.sid = retb.get('sid')

            auth = ET.Element("auth", {
                "xmlns": SASL_XMLNS,
                "mechanism": "PLAIN",
            })
            sasl_str = "\000%s\000%s" % (self.jid.localpart, self.password)
            auth.text = base64.b64encode(sasl_str.encode(encoding="utf-8")).decode("utf-8")
            retb, elems = self.send_body(self.build_body(auth))

            if not elems:
                # poll for data
                retb, elems = self.send_body(self.build_body())

            if retb.find("{%s}success" % SASL_XMLNS) is not None:
                retb, elems = self.send_body(self.build_body())

                if next(retb.iter("{%s}bind" % BIND_XMLNS)):

                    iq = ET.Element("iq", {
                        "xmlns": "jabber:client",
                        "type": "set",
                        "id": str(uuid.uuid4()),
                    })
                    bind = ET.SubElement(iq, "bind")
                    bind.set("xmlns", BIND_XMLNS)

                    if self.jid.resource:
                        resource = ET.SubElement(bind, "resource")
                        resource.text(self.jid.resource)

                    retb, elems = self.send_body(self.build_body(iq))

                    # send session
                    iq = ET.Element("iq", {
                        "xmlns": "jabber:client",
                        "type": "set",
                        "id": str(uuid.uuid4()),
                    })
                    session = ET.SubElement(iq, "session")
                    session.set("xmlns", SESSION_XMLNS)
                    retb, elems = self.send_body(self.build_body(iq))

                    self.logged_in = True
                    self.rid += 1
