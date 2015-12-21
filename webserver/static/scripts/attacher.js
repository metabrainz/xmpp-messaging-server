require("strophe");
// Documentation for Strophe.js is available at http://strophe.im/strophejs/doc/1.2.3

console.log("Attacher started!");

// TODO: Allow to modify the address here:
Attacher.connection = new Strophe.Connection("http://localhost:5280/http-bind");
Attacher.connection.rawInput = function (data) {
  console.log("XMPP RECV: ", data);
};
Attacher.connection.rawOutput = function (data) {
  console.log("XMPP SENT: ", data);
};

Attacher.connection.attach(
    Attacher.JID,
    Attacher.SID,
    Attacher.RID, function (arg) {
      console.log("Session attached!", arg);
    }
);

Attacher.connection.sendIQ(
    $iq({
      to: Strophe.getDomainFromJid(Attacher.JID),
      type: "get"
    })
        .c('query', {
          xmlns: 'http://jabber.org/protocol/disco#info'
        }),
    function (arg) {
      console.log("IQ callback", arg);
    },
    function (arg) {
      console.log("IQ errback", arg);
    }
);

function sendTestMessage(body) {
  let reply = $msg({
    to: "test@localhost",
    type: 'chat'
  })
      .cnode(Strophe.xmlElement('body', body)).up()
      .c('active', {xmlns: "http://jabber.org/protocol/chatstates"});
  Attacher.connection.send(reply);
}

sendTestMessage("I'm attached!");
