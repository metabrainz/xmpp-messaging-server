class JID:
    """Helper class for working with JIDs.

    See https://tools.ietf.org/html/rfc6122.
    """

    def __init__(self, jid_string):
        # TODO: make this more robust
        at_idx = jid_string.index("@")
        self.localpart = jid_string[:at_idx]

        # Everything after `@`
        second_part = jid_string[at_idx+1:]
        res_start_idx = second_part.find("/")

        if res_start_idx == -1:
            self.domainpart = second_part
            self.resource = None
        else:
            self.domainpart = second_part[:res_start_idx]
            self.resource = second_part[res_start_idx+1:]

    @property
    def full(self):
        string = "{localpart}@{domainpart}"
        if self.resource:
            string += "/" + self.resource
        return string
