from webserver.xmpp.exceptions import XMPPClientException
from xml.etree import ElementTree as ET
from sleekxmpp.jid import JID
import requests
import random
import base64
import uuid

XMLNS_BOSH = "http://jabber.org/protocol/httpbind"
XMLNS_TLS = "urn:ietf:params:xml:ns:xmpp-tls"
XMLNS_SASL = "urn:ietf:params:xml:ns:xmpp-sasl"
XMLNS_BIND = "urn:ietf:params:xml:ns:xmpp-bind"
XMLNS_SESSION = "urn:ietf:params:xml:ns:xmpp-session"
XMLNS_STREAM = "http://etherx.jabber.org/streams"
XMLNS_XMPP_IQ = "jabber:client"


class BOSHSession:

    def __init__(self, bosh_service, jid, password):
        self.rid = random.randint(0, 1000000000)  # See https://xmpp.org/extensions/xep-0124.html#rids
        self.authid = None
        self.sid = None
        self.logged_in = False

        self.bosh_service = bosh_service
        self.jid = JID(jid)
        self.password = password

    def start_session_and_auth(self, hold=1, wait=60):
        body = ET.Element("body", {
            "content": "text/xml; charset=utf-8",
            "xml:lang": "en",
            "xmlns": XMLNS_BOSH,
            "xmlns:xmpp": "urn:xmpp:xbosh",
            "xmpp:version": "1.0",
            "rid": str(self.rid),
            "to": self.jid.domain,
            "hold": str(hold),
            "wait": str(wait),
        })

        ret_xml, ret_elems = self._send_body(body)

        if type(ret_xml) != str and ret_xml.get('authid') and ret_xml.get('sid'):
            self.authid = ret_xml.get('authid')
            self.sid = ret_xml.get('sid')

            # TODO: Use other authentication mechanism!
            auth = ET.Element("auth", {
                "xmlns": XMLNS_SASL,
                "mechanism": "PLAIN",
            })
            sasl_str = "\000%s\000%s" % (self.jid.local, self.password)
            auth.text = base64.b64encode(sasl_str.encode(encoding="utf-8")).decode("utf-8")
            ret_xml, ret_elems = self._send_body(self._build_body(auth))

            if not ret_elems:
                # Poll for data
                ret_xml, ret_elems = self._send_body(self._build_body())

            if ret_xml.find("{%s}success" % XMLNS_SASL) is not None:
                ret_xml, ret_elems = self._send_body(self._build_body())

                ret_features = ret_xml.find("{%s}features" % XMLNS_STREAM)
                if ret_features and ret_features.find("{%s}bind" % XMLNS_BIND) is not None:
                    self._bind_resource()
                    self._establish_session()

                    self.logged_in = True
                    self.rid += 1

    def _bind_resource(self):
        iq = ET.Element("iq", {
            "xmlns": XMLNS_XMPP_IQ,
            "type": "set",
            "id": str(uuid.uuid4()),
        })
        bind = ET.SubElement(iq, "bind")
        bind.set("xmlns", XMLNS_BIND)

        if self.jid.resource:
            resource = ET.SubElement(bind, "resource")
            resource.text = self.jid.resource

        retb, elems = self._send_body(self._build_body(iq))

    def _establish_session(self):
        """Establish session for connection."""
        iq_id = str(uuid.uuid4())
        iq = ET.Element("iq", {
            "xmlns": XMLNS_XMPP_IQ,
            "type": "set",
            "id": iq_id,
        })
        session = ET.SubElement(iq, "session")
        session.set("xmlns", XMLNS_SESSION)
        ret_xml, ret_elems = self._send_body(self._build_body(iq))

        # Validation
        ret_iq = ret_xml.find("{%s}iq" % XMLNS_XMPP_IQ)
        if ret_iq is None:
            raise XMPPClientException(
                    "Failed to establish a session."
                    "Can't find `iq` element in server response."
            )
        else:
            ret_iq_type = ret_iq.get("type")
            if ret_iq_type != "result":
                raise XMPPClientException(
                        "Failed to establish a session."
                        "Unexpected `type` returned: '%s'." % ret_iq_type
                )
            ret_iq_id = ret_iq.get("id")
            if ret_iq_id != iq_id:
                raise XMPPClientException(
                        "Failed to establish a session."
                        "Unexpected `id` returned: '%s'. Expected: '%s'."
                        % (ret_iq_id, iq_id)
                )

    def _send_body(self, body):
        # TODO: Find a better way to get rid of declaration here:
        body_str = ET.tostring(body, encoding="utf8", method="xml")[len("<?xml version='1.0' encoding='utf8'?>") + 1:]
        resp = requests.post(
                self.bosh_service,
                data=body_str,
                headers={
                    "Content-type": "text/xml; charset=utf-8",
                    "Accept": "text/xml",
                },
        )
        if resp.status_code == 200:
            resp_xml = ET.fromstring(resp.text)
            return resp_xml, list(resp_xml)
        else:
            raise XMPPClientException("Failed to send body. %s" % resp)

    def _build_body(self, child=None):
        """Build a BOSH body."""
        self.rid += 1
        body = ET.Element("body", {
            "content": "text/xml; charset=utf-8",
            "xml:lang": "en",
            "xmlns": XMLNS_BOSH,
            "rid": str(self.rid),
            "sid": self.sid,
        })
        if child is not None:
            body.append(child)
        return body
